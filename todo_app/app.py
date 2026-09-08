"""Todo app web server."""

import base64
import os
import time
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DEFAULT_PORT = 8000
IMAGE_FILE = Path(os.getenv("IMAGE_FILE", "/usr/src/app/files/image.jpg"))
IMAGE_MAX_AGE_SECONDS = 600
IMAGE_URL = "https://picsum.photos/1200"

app = FastAPI(title="todo-app")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

todos = [
    "Read the course material",
    "Write a todo app",
]


def image_is_stale() -> bool:
    try:
        age = time.time() - IMAGE_FILE.stat().st_mtime
    except FileNotFoundError:
        return True
    return age > IMAGE_MAX_AGE_SECONDS


async def fetch_image() -> None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        response = await client.get(IMAGE_URL)
        response.raise_for_status()

    IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temporary file first so a request never reads a half-written
    # image, then swap it in with an atomic rename.
    staging = IMAGE_FILE.with_suffix(".tmp")
    staging.write_bytes(response.content)
    staging.replace(IMAGE_FILE)


async def image_data_uri() -> str | None:
    """The cached picture, inlined into the page. None if we have none yet."""
    if image_is_stale():
        try:
            await fetch_image()
        except httpx.HTTPError:
            # Serving the previous picture beats serving none at all.
            pass

    try:
        encoded = base64.b64encode(IMAGE_FILE.read_bytes()).decode()
    except FileNotFoundError:
        return None
    return f"data:image/jpeg;base64,{encoded}"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": todos, "image": await image_data_uri()},
    )


def main() -> None:
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
