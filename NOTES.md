# What I checked, and what the agent got wrong

## What the agent got wrong
Sweeping the helper files for dead code was the riskiest step. Three functions in
fleet_utils.py (`is_due`, `parse_service_date`, `chunk_list`) and `log_util.debug`/`DEBUG`
had explicit comments saying they were unused or dead, and a grep confirmed zero call
sites, so deleting those was safe. But `fleet_utils.mean()` and `format_percent()` also had
zero call sites at that point in the repo, with no comment marking them as dead — they were
only unused because `fleet_report.fleet_summary` had its own buggy inline average
(`total // len(fleet)`) instead of calling them. If the agent had applied the same "zero
callers = delete it" rule mechanically, it would have removed two genuinely useful
functions along with the three actually-dead ones. Instead it wired `mean()` and
`format_percent()` into the fixed `fleet_summary`/`print_report`, which is the right call,
but it's exactly the kind of thing I had to check rather than accept on faith — "nothing
calls this" and "this is dead code" are not the same claim.

The agent also made a judgment call that no test forces: when a car has no
`last_service_km` reading, `fleet_summary` now excludes it from the average-wear
calculation (unknown wear, not zero) while still counting it in the total car count and
never marking it as due. That's a reasonable interpretation of "don't crash and don't treat
it as fully worn," but it's a design decision, not something `verify.py` pins down
numerically, so I had to read the code to confirm it does something sensible rather than
just confirm it doesn't crash.

## What I checked before I accepted its work
- Ran `pytest` myself (4/4 pass, including the new missing-reading test) and `python
  verify.py` myself (10/11 pass) rather than trusting the agent's summary of the results.
- Grepped the whole repo for every function the agent proposed deleting
  (`is_due`, `parse_service_date`, `chunk_list`, `debug`/`DEBUG`, `get_setting`) to confirm
  there were really zero remaining call sites, instead of trusting "this looks unused."
- Confirmed the 15,000 km interval, the 80% threshold, and the settings.cfg values are
  byte-for-byte unchanged — both via `verify.py`'s two "rules are unchanged" checks and by
  reading `km_wachter.py` and `settings.cfg` myself.
- Hand-checked the two headline bug fixes' arithmetic: 14,900 / 15,000 * 100 ≈ 99.3%
  (matches what the wear-percent test expects), and 100 km * 0.621371 ≈ 62.1 miles (matches
  the range `verify.py` checks for), so the fixes use the actually-correct constants, not
  just numbers that happen to pass.

## What the data actually said
`odometer_km` (total mileage) and `age_years` do **not** predict breakdown in
`fleet_history.csv` — the group means are nearly identical (53,302 km vs. 53,448 km for
cars that didn't/did break down; 5.89 vs. 5.88 years), with an effect size close to zero for
both. That's exactly the "older, higher-mileage cars break down" assumption TASK.md warned
against, and the data doesn't support it.

The factors that do separate the two groups are `km_since_service` (how overdue the car is
for its next service — by far the strongest signal, effect size ≈0.98), `avg_daily_km`
(≈0.61), and `load_factor` (≈0.52). `analyze.py` builds its 0–100 risk score only from those
three, weighted by effect size, which lets it flag cars that are high-risk before the 80%
service rule would ever catch them — several of the highest-risk cars in the ranked output
aren't yet due under the interval rule at all.
