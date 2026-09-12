"""Todo backend: stores the todo items."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import asyncpg
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

PORT = int(os.getenv("SERVER_PORT", 8000))
MAX_TODO_LENGTH = int(os.getenv("MAX_TODO_LENGTH", 140))

DB_HOST = os.getenv("DB_HOST", "postgres-svc")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "todo")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

CONNECT_ATTEMPTS = 10
CONNECT_RETRY_SECONDS = 3

# A rejected todo can be arbitrarily long, so keep the log line readable.
LOGGED_TODO_LIMIT = 200

# Match uvicorn's own format so the lines read as one log.
logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger("todo-backend")


async def connect() -> asyncpg.Pool:
    """Wait for the database, then make sure the todos table exists."""
    for attempt in range(1, CONNECT_ATTEMPTS + 1):
        try:
            pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            break
        except (OSError, asyncpg.PostgresError) as error:
            if attempt == CONNECT_ATTEMPTS:
                raise
            logger.warning("Database not ready (%s), retrying", error)
            await asyncio.sleep(CONNECT_RETRY_SECONDS)

    async with pool.acquire() as connection:
        await connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                todo VARCHAR({MAX_TODO_LENGTH}) NOT NULL
            )
            """
        )

    return pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await connect()
    yield
    await app.state.pool.close()


app = FastAPI(title="todo-backend", lifespan=lifespan)


class NewTodo(BaseModel):
    todo: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


@app.exception_handler(RequestValidationError)
async def log_rejected_todo(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Validation failures never reach the route, so log them here."""
    body = exc.body if isinstance(exc.body, dict) else {}
    todo = str(body.get("todo", ""))
    reasons = "; ".join(error["msg"] for error in exc.errors())
    logger.warning(
        "Rejected todo (%s characters): %r — %s",
        len(todo),
        todo[:LOGGED_TODO_LIMIT],
        reasons,
    )
    return await request_validation_exception_handler(request, exc)


@app.get("/todos")
async def read_todos() -> list[str]:
    rows = await app.state.pool.fetch("SELECT todo FROM todos ORDER BY id")
    return [row["todo"] for row in rows]


@app.post("/todos", status_code=201)
async def create_todo(new_todo: NewTodo) -> str:
    await app.state.pool.execute(
        "INSERT INTO todos (todo) VALUES ($1)", new_todo.todo
    )
    logger.info("Created todo: %r", new_todo.todo)
    return new_todo.todo


def main() -> None:
    logger.info("Server started in port %s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
