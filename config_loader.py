# config_loader.py
# Reads settings.cfg (hand-rolled key=value parsing, no ConfigParser).

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Parse settings.cfg into a dict of strings. Unknown keys and malformed
    lines are dropped silently, matching the original 2013 behaviour."""
    if path is None:
        path = SETTINGS_FILE
    settings = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as an int, or fallback if missing/not a valid int."""
    try:
        return int(settings[key])
    except (KeyError, ValueError):
        return fallback
