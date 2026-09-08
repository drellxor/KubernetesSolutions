"""Logs a random string every 5 seconds and serves it over HTTP."""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

DEFAULT_PORT = 8000
INTERVAL_SECONDS = 5

random_string = str(uuid.uuid4())


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def status() -> str:
    return f"{timestamp()}: {random_string}"


async def log_loop() -> None:
    while True:
        print(status(), flush=True)
        await asyncio.sleep(INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(log_loop())
    yield
    task.cancel()


app = FastAPI(title="log-output", lifespan=lifespan)


@app.get("/", response_class=PlainTextResponse)
@app.get("/status", response_class=PlainTextResponse)
async def read_status() -> str:
    return status()


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
