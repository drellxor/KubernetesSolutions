# todo_backend

Stores the todo items for the todo app. The list is kept in memory, so it
resets whenever the app restarts.

## Endpoints

- `GET /todos` — the list of todos, as JSON.
- `POST /todos` — add one, body `{"todo": "..."}`. Rejects empty todos and
  anything over 140 characters with a 422.

The port is read from the `PORT` environment variable, defaulting to 8000.

## Run locally

```sh
pip install -r todo_backend/requirements.txt
PORT=3000 python3 todo_backend/app.py
```

## Run with Docker

```sh
docker build -t todo-backend todo_backend
docker run --rm -e PORT=3000 -p 3000:3000 todo-backend
```
