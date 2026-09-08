# log_output

Generates a random string (UUID v4) on startup, keeps it in memory, prints it
with a timestamp every 5 seconds, and serves the same status over HTTP.

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
2020-03-30T12:15:22.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
```

## Endpoints

- `GET /` and `GET /status` — current timestamp and the random string, as plain text.

The port is read from the `PORT` environment variable, defaulting to 8000.

## Run locally

```sh
pip install -r log_output/requirements.txt
PORT=3000 python3 log_output/app.py
```

## Run with Docker

```sh
docker build -t log-output log_output
docker run --rm -e PORT=3000 -p 3000:3000 log-output
```
