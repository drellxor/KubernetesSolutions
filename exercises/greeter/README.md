# greeter

Answers every GET with a greeting. log_output shows it on its status page.

Two versions run side by side from the same image: `greeter-v1` and
`greeter-v2` differ only in their `version` label and `GREETING`. log_output
calls `greeter-svc`, and an HTTPRoute attached to that Service sends 75% of the
requests to `greeter-svc-1` and 25% to `greeter-svc-2`. The route is L7, so it
only takes effect through the namespace's waypoint.

## Configuration

- `SERVER_PORT` — port the server listens on, default 8000.
- `GREETING` — the response body, default `Hello`.

## Endpoints

- `GET /` — plain text greeting.
- `GET /healthz` — `ok`.

## Run locally

```sh
pip install -r exercises/greeter/requirements.txt
GREETING="Hello from version 1" SERVER_PORT=3000 python3 exercises/greeter/app.py
```
