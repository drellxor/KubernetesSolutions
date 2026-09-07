"""Todo app web server."""

import os

import uvicorn
from fastapi import FastAPI

DEFAULT_PORT = 8000

app = FastAPI(title="todo-app")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "todo app"}


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
