# todo_app

Serves the todo page. The todos themselves live in the todo_backend service,
which this app reads from and posts to. On startup it prints
`Server started in port NNNN`.

The page shows a random picture from [Lorem Picsum](https://picsum.photos),
cached on disk and refreshed when it is more than 10 minutes old.

## Configuration

- `PORT` — port the server listens on, default 8000.
- `TODO_BACKEND_URL` — where the todo_backend service lives, default
  `http://todo-backend-svc:2349`.
- `IMAGE_FILE` — where the cached picture is stored, default
  `/usr/src/app/files/image.jpg`. Mount a volume at that directory so the
  cache survives restarts.

## Run locally

```sh
pip install -r todo_app/requirements.txt
IMAGE_FILE=/tmp/image.jpg PORT=3000 python3 todo_app/app.py
```

## Run with Docker

```sh
docker build -t todo-app todo_app
docker run --rm -e PORT=3000 -p 3000:3000 todo-app
```
