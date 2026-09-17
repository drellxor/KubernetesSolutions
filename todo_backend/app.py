"""Todo backend: stores the todo items."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import asyncpg
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException
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
                todo VARCHAR({MAX_TODO_LENGTH}) NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        # CREATE TABLE IF NOT EXISTS leaves an older table untouched, so add
        # the column separately for databases that predate it.
        await connection.execute(
            "ALTER TABLE todos ADD COLUMN IF NOT EXISTS done BOOLEAN NOT NULL DEFAULT FALSE"
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


class TodoUpdate(BaseModel):
    done: bool


class Todo(BaseModel):
    id: int
    todo: str
    done: bool


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

@app.get("/")
async def root() -> str:
    return "OK"


@app.get("/healthz")
async def health() -> str:
    try:
        await app.state.pool.fetchval("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return "ok"


@app.get("/todos")
async def read_todos() -> list[Todo]:
    rows = await app.state.pool.fetch("SELECT id, todo, done FROM todos ORDER BY id")
    return [Todo(**dict(row)) for row in rows]


@app.post("/todos", status_code=201)
async def create_todo(new_todo: NewTodo) -> Todo:
    row = await app.state.pool.fetchrow(
        "INSERT INTO todos (todo) VALUES ($1) RETURNING id, todo, done", new_todo.todo
    )
    logger.info("Created todo: %r", new_todo.todo)
    return Todo(**dict(row))


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, update: TodoUpdate) -> Todo:
    row = await app.state.pool.fetchrow(
        "UPDATE todos SET done = $1 WHERE id = $2 RETURNING id, todo, done",
        update.done,
        todo_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="no such todo")

    logger.info("Todo %s marked %s", todo_id, "done" if update.done else "not done")
    return Todo(**dict(row))


def main() -> None:
    logger.info("Server started in port %s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
