# ping_pong

Responds `pong N` to a GET request, where N counts the requests answered so
far. The count is written to a file on a shared volume, where the log_output
app reads it.

## Configuration

- `PORT` — port the server listens on, default 8000.
- `COUNTER_FILE` — where the request count is stored, default
  `/usr/src/app/files/pingpong.txt`.

## Endpoints

- `GET /` and `GET /pingpong` — plain text `pong N`.

## Run locally

```sh
pip install -r ping_pong/requirements.txt
COUNTER_FILE=/tmp/pingpong.txt PORT=3000 python3 ping_pong/app.py
```

## Run with Docker

```sh
docker build -t ping-pong ping_pong
docker run --rm -e PORT=3000 -p 3000:3000 ping-pong
```
