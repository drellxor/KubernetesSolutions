# log_output

Split into two containers that share a volume:

- `writer.py` — generates a random string (UUID v4) on startup and appends it
  with a timestamp to a file every 5 seconds.
- `server.py` — serves the contents of that file over HTTP.

Both use the same image; the container's `command` selects which one runs.
`server.py` is the image's default.

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
2020-03-30T12:15:22.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
```

## Configuration

- `PORT` — port the server listens on, default 8000.
- `LOG_FILE` — the shared file, default `/usr/src/app/files/log.txt`.
  Both containers must agree on this path and mount the same volume there.

## Endpoints

- `GET /` and `GET /status` — the file contents, as plain text.

## Run locally

```sh
pip install -r log_output/requirements.txt
LOG_FILE=/tmp/log.txt python3 log_output/writer.py &
LOG_FILE=/tmp/log.txt PORT=3000 python3 log_output/server.py
```

## Run with Docker

```sh
docker build -t log-output log_output
docker volume create log-output-files

docker run -d -v log-output-files:/usr/src/app/files log-output python3 writer.py
docker run -d -v log-output-files:/usr/src/app/files -e PORT=3000 -p 3000:3000 log-output
```
