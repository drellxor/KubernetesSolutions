"""Writes a random string with a timestamp to a file every 5 seconds."""

import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

INTERVAL_SECONDS = 5
LOG_FILE = Path(os.getenv("LOG_FILE", "/usr/src/app/files/log.txt"))


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def main() -> None:
    random_string = str(uuid.uuid4())
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    while True:
        line = f"{timestamp()}: {random_string}"
        with LOG_FILE.open("a") as f:
            f.write(f"{line}\n")
        print(line, flush=True)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
