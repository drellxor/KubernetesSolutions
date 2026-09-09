"""Todo backend: stores the todo items."""

import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

DEFAULT_PORT = 8000
MAX_TODO_LENGTH = 140

app = FastAPI(title="todo-backend")

todos: list[str] = [
    "Read the course material",
    "Write a todo app",
    "Deploy it to Kubernetes",
]


class NewTodo(BaseModel):
    todo: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


@app.get("/todos")
async def read_todos() -> list[str]:
    return todos


@app.post("/todos", status_code=201)
async def create_todo(new_todo: NewTodo) -> str:
    todos.append(new_todo.todo)
    return new_todo.todo


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
