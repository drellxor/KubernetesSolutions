"""Ping-pong app: counts the requests it has answered."""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

DEFAULT_PORT = 8000
COUNTER_FILE = Path(os.getenv("COUNTER_FILE", "/usr/src/app/files/pingpong.txt"))

app = FastAPI(title="ping-pong")


def read_counter() -> int:
    """Pick up where a previous run left off, if the volume already has a count."""
    try:
        return int(COUNTER_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


counter = read_counter()


@app.get("/", response_class=PlainTextResponse)
@app.get("/pingpong", response_class=PlainTextResponse)
async def pingpong() -> str:
    global counter
    response = f"pong {counter}"
    counter += 1
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(f"{counter}\n")
    return response


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
