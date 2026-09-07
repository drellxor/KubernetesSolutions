# log_output

Generates a random string (UUID v4) on startup, keeps it in memory, and prints
it with a timestamp every 5 seconds.

Example output:

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
2020-03-30T12:15:22.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
```

## Run locally

```sh
python3 log_output/app.py
```

## Run with Docker

```sh
docker build -t log-output log_output
docker run --rm log-output
```
