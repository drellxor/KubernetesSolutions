"""Generates a random string on startup and logs it every 5 seconds."""

import signal
import threading
import uuid
from datetime import datetime, timezone

INTERVAL_SECONDS = 5

shutdown = threading.Event()


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def main() -> None:
    # As PID 1 in a container, signals without an explicit handler are ignored,
    # so handle SIGTERM to exit promptly on `docker stop` / pod termination.
    signal.signal(signal.SIGTERM, lambda *_: shutdown.set())
    signal.signal(signal.SIGINT, lambda *_: shutdown.set())

    random_string = str(uuid.uuid4())
    while not shutdown.is_set():
        print(f"{timestamp()}: {random_string}", flush=True)
        shutdown.wait(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
