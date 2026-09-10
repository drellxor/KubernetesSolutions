"""Ping-pong app: counts the requests it has answered."""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

PORT = int(os.getenv("SERVER_PORT", 8000))
CONFIG_FILE = Path(os.getenv("CONFIG_FILE", "/config/ping_pong_db.config"))

CONNECT_ATTEMPTS = 10
CONNECT_RETRY_SECONDS = 3


def read_config() -> dict[str, str]:
    """Parse the key=value lines of the mounted database config."""
    config = {}
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()
    return config


async def connect() -> asyncpg.Pool:
    """Wait for the database, then make sure our single counter row exists."""
    config = read_config()

    for attempt in range(1, CONNECT_ATTEMPTS + 1):
        try:
            pool = await asyncpg.create_pool(
                host=config["db_host"],
                port=int(config["db_port"]),
                database=config["db"],
                user=config["user"],
                password=config["password"],
            )
            break
        except (OSError, asyncpg.PostgresError) as error:
            if attempt == CONNECT_ATTEMPTS:
                raise
            print(f"Database not ready ({error}), retrying", flush=True)
            await asyncio.sleep(CONNECT_RETRY_SECONDS)

    async with pool.acquire() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pingpong (
                id INTEGER PRIMARY KEY,
                counter INTEGER NOT NULL
            )
            """
        )
        await connection.execute(
            "INSERT INTO pingpong (id, counter) VALUES (1, 0) ON CONFLICT DO NOTHING"
        )

    return pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await connect()
    yield
    await app.state.pool.close()


app = FastAPI(title="ping-pong", lifespan=lifespan)


@app.get("/", response_class=PlainTextResponse)
@app.get("/pingpong", response_class=PlainTextResponse)
async def pingpong() -> str:
    # One statement, so concurrent requests cannot hand out the same number.
    counter = await app.state.pool.fetchval(
        "UPDATE pingpong SET counter = counter + 1 WHERE id = 1 RETURNING counter"
    )
    return f"pong {counter - 1}"


@app.get("/pings", response_class=PlainTextResponse)
async def pings() -> str:
    counter = await app.state.pool.fetchval(
        "SELECT counter FROM pingpong WHERE id = 1"
    )
    return f"{counter}"


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
