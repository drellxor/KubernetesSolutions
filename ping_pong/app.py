"""Ping-pong app: counts the requests it has answered."""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

DEFAULT_PORT = 8000

app = FastAPI(title="ping-pong")

counter = 0


@app.get("/", response_class=PlainTextResponse)
@app.get("/pingpong", response_class=PlainTextResponse)
async def pingpong() -> str:
    global counter
    response = f"pong {counter}"
    counter += 1
    return response


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
