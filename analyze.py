# analyze.py
# Make KM-Waechter smarter. The 80% rule only warns you once a car is nearly worn. Here we find
# which cars are most likely to break down SOON, from their history, and rank them by risk, so the
# fleet team can fix the risky ones before the 80% rule would ever flag them.
#
# Summary: km_since_service, avg_daily_km, and load_factor separate the cars that broke down
# from the ones that didn't. odometer_km (total mileage) and age_years do NOT -- their group
# means are nearly identical, so "older, higher-mileage cars break down" is not what this data
# says. The risk score below is built only from the factors that actually separate the groups.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

FEATURE_COLUMNS = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

# Step 1: compare the two groups column by column, instead of assuming which ones matter.
broke_down = df[df["broke_down"] == 1]
still_ok = df[df["broke_down"] == 0]

print("Comparing cars that broke down vs. cars that didn't:")
print(f"{'column':<18}{'mean (ok)':>12}{'mean (broke)':>14}{'effect size':>14}")
effect_sizes = {}
for col in FEATURE_COLUMNS:
    pooled_std = df[col].std()
    effect = (broke_down[col].mean() - still_ok[col].mean()) / pooled_std
    effect_sizes[col] = effect
    print(f"{col:<18}{still_ok[col].mean():>12.1f}{broke_down[col].mean():>14.1f}{effect:>14.3f}")

# Step 2: keep only the columns that actually separate the groups (|effect size| >= 0.2 is a
# small-to-medium effect; anything weaker than that is noise, not a real risk factor).
risk_factors = {c: abs(e) for c, e in effect_sizes.items() if abs(e) >= 0.2}
dropped = [c for c in FEATURE_COLUMNS if c not in risk_factors]
print(f"\nUsed for risk score: {list(risk_factors)}")
print(f"Dropped (do not separate the groups): {dropped}")

# Step 3: build a simple 0-100 risk score -- each kept factor is min-max scaled to 0-100 across
# the fleet, then combined with weights proportional to how strongly it separates the groups.
total_weight = sum(risk_factors.values())
weights = {c: w / total_weight for c, w in risk_factors.items()}

df["risk_score"] = 0.0
for col, weight in weights.items():
    lo, hi = df[col].min(), df[col].max()
    scaled = (df[col] - lo) / (hi - lo) * 100
    df["risk_score"] += scaled * weight
df["risk_score"] = df["risk_score"].round(1)

# Step 4: rank by risk, highest first, and show which cars the 80% service rule wouldn't catch
# yet -- these are the ones this analysis surfaces earlier than KM-Waechter's own flag.
SERVICE_INTERVAL_KM = 15000  # must match km_wachter.SERVICE_INTERVAL_KM, do not change
WARN_AT_PERCENT = 80  # must match km_wachter.WARN_AT_PERCENT, do not change
df["already_flagged_by_80pct_rule"] = (df["km_since_service"] / SERVICE_INTERVAL_KM * 100) >= WARN_AT_PERCENT

ranked = df.sort_values("risk_score", ascending=False)
print("\nFleet ranked by breakdown risk (highest first):")
print(f"{'car_id':<10}{'risk_score':>11}{'km_since_service':>18}{'avg_daily_km':>14}{'load_factor':>13}{'80pct_rule':>12}")
for _, row in ranked.iterrows():
    flagged = "yes" if row["already_flagged_by_80pct_rule"] else "no"
    print(
        f"{row['car_id']:<10}{row['risk_score']:>11.1f}{row['km_since_service']:>18.0f}"
        f"{row['avg_daily_km']:>14.0f}{row['load_factor']:>13.2f}{flagged:>12}"
    )

not_yet_flagged = ranked[~ranked["already_flagged_by_80pct_rule"]]
print(
    f"\n{len(not_yet_flagged)} of {len(ranked)} cars are not yet due under the 80% rule; "
    f"the {min(10, len(not_yet_flagged))} riskiest of those are worth fixing early:"
)
print(not_yet_flagged.head(10)[["car_id", "risk_score"]].to_string(index=False))
