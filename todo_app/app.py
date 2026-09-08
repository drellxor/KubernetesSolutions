"""Todo app web server."""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DEFAULT_PORT = 8000

app = FastAPI(title="todo-app")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

todos = [
    "Read the course material",
    "Write a todo app",
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="index.html", context={"todos": todos}
    )


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
