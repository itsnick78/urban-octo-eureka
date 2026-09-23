# log_util.py
# A small homemade logger (predates use of the standard logging module here).

import time

LOG_LINES = []                          # global state, shared by everyone who imports this


def log(message: str) -> None:
    """Timestamp a message, print it, and buffer it for flush_log()."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append all buffered log lines to path, then clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
