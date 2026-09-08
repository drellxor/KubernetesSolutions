"""Serves the file written by writer.py, with the ping-pong request count."""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

DEFAULT_PORT = 8000
LOG_FILE = Path(os.getenv("LOG_FILE", "/usr/src/app/files/log.txt"))
COUNTER_FILE = Path(os.getenv("COUNTER_FILE", "/usr/src/app/files/pingpong.txt"))

app = FastAPI(title="log-output")


def latest_log_line() -> str:
    try:
        lines = LOG_FILE.read_text().splitlines()
    except FileNotFoundError:
        return "no output yet"
    return lines[-1] if lines else "no output yet"


def pingpong_count() -> int:
    try:
        return int(COUNTER_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


@app.get("/", response_class=PlainTextResponse)
@app.get("/status", response_class=PlainTextResponse)
async def read_status() -> str:
    return f"{latest_log_line()}.\nPing / Pongs: {pingpong_count()}"


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
