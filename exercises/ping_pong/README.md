# ping_pong

Responds `pong N` to a GET request, where N counts the requests answered so
far. The count lives in a PostgreSQL database, so it survives restarts of
both the app and the database.

## Configuration

- `SERVER_PORT` — port the server listens on, default 8000.
- `CONFIG_FILE` — the database settings, default `/config/ping_pong_db.config`,
  mounted from the `exercises-config` ConfigMap. It holds one `key=value` per
  line:

```
db_host=postgres-svc
db_port=5432
db=ping_pong
user=postgres
password=postgres
```

The app creates its `pingpong` table on startup, retrying while the database
comes up.

## Serverless

In the cluster it runs as a Knative Service (`manifests/knative-service.yaml`),
so it scales to zero when idle and starts again on the next request; the count
survives because it lives in Postgres. It is cluster-local, at
`http://ping-pong.exercises.svc.cluster.local`. Knative routes by Host header,
so callers must use that full name, and the exercises gateway rewrites the Host
for `/pingpong`.

The image is named `dev.local/exercises/ping-pong`: Knative looks up every
image tag in its registry unless the registry is `dev.local`, and this image
is built locally and loaded with `k3d image import`.

## Endpoints

- `GET /` and `GET /pingpong` — plain text `pong N`, and increments the count.
- `GET /pings` — the current count, without incrementing.

## Run locally

Start a database, write a config file pointing at it, then:

```sh
pip install -r exercises/ping_pong/requirements.txt
CONFIG_FILE=./ping_pong_db.config SERVER_PORT=3000 python3 exercises/ping_pong/app.py
```

## Run with Docker

```sh
docker build -t ping-pong exercises/ping_pong
docker run --rm -v "$PWD/config:/config:ro" -e SERVER_PORT=3000 -p 3000:3000 ping-pong
```
