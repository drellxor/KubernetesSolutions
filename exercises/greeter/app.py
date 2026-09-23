"""Greeter: answers every GET with a greeting. The version is set by GREETING."""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

PORT = int(os.getenv("SERVER_PORT", 8000))
GREETING = os.getenv("GREETING", "Hello")

app = FastAPI(title="greeter")


@app.get("/", response_class=PlainTextResponse)
async def greet() -> str:
    return GREETING


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz() -> str:
    return "ok"


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
