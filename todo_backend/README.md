# todo_backend

Stores the todo items for the todo app in a PostgreSQL database, so they
survive restarts of both the app and the database.

## Endpoints

- `GET /todos` — the list of todos, as JSON.
- `POST /todos` — add one, body `{"todo": "..."}`. Rejects empty todos and
  anything over `MAX_TODO_LENGTH` characters with a 422.

`create_todo.py` is a one-off script, meant to be run as a job: it picks a
random Wikipedia article and posts `Read <URL>` to the API, then exits.

```sh
docker run --rm -e TODO_BACKEND_URL=... todo-backend python3 create_todo.py
```

## Configuration

- `SERVER_PORT` — port the server listens on, default 8000.
- `MAX_TODO_LENGTH` — longest accepted todo, default 140.
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` — the database.
- `TODO_BACKEND_URL` — used by `create_todo.py` to reach the API, default
  `http://todo-backend-svc:2349`.

The app creates its `todos` table on startup, retrying while the database
comes up.

## Run locally

Start a database, then:

```sh
pip install -r todo_backend/requirements.txt
DB_HOST=localhost SERVER_PORT=3000 python3 todo_backend/app.py
```

## Run with Docker

```sh
docker build -t todo-backend todo_backend
docker run --rm -e SERVER_PORT=3000 -e DB_HOST=... -p 3000:3000 todo-backend
```
