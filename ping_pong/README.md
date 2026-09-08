# ping_pong

Responds `pong N` to a GET request, where N counts the requests answered so
far. The counter lives in memory, so it resets whenever the app restarts.

## Endpoints

- `GET /` and `GET /pingpong` — plain text `pong N`.

The port is read from the `PORT` environment variable, defaulting to 8000.

## Run locally

```sh
pip install -r ping_pong/requirements.txt
PORT=3000 python3 ping_pong/app.py
```

## Run with Docker

```sh
docker build -t ping-pong ping_pong
docker run --rm -e PORT=3000 -p 3000:3000 ping-pong
```
