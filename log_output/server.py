"""Serves the contents of the file written by writer.py."""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

DEFAULT_PORT = 8000
LOG_FILE = Path(os.getenv("LOG_FILE", "/usr/src/app/files/log.txt"))

app = FastAPI(title="log-output")


@app.get("/", response_class=PlainTextResponse)
@app.get("/status", response_class=PlainTextResponse)
async def read_status() -> str:
    if not LOG_FILE.exists():
        return "no output yet"
    return LOG_FILE.read_text()


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
