# todo_app

Web server that will grow into a todo application. On startup it prints
`Server started in port NNNN`.

The port is read from the `PORT` environment variable, defaulting to 8000.

## Run locally

```sh
pip install -r todo_app/requirements.txt
PORT=3000 python3 todo_app/app.py
```

## Run with Docker

```sh
docker build -t todo-app todo_app
docker run --rm -e PORT=3000 -p 3000:3000 todo-app
```
