# broadcaster

Subscribes to todo events on NATS and forwards them to a Telegram chat.

Replicas all join the same NATS **queue group**, so each message is delivered
to exactly one of them. Scaling up spreads the work rather than duplicating it.

## Configuration

- `NATS_URL` — default `nats://my-nats.nats.svc.cluster.local:4222`.
- `NATS_SUBJECT` — default `todos`, must match what the backend publishes on.
- `NATS_QUEUE_GROUP` — default `broadcaster`. Every replica must share it.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — required; the app exits without them.
- `TELEGRAM_API_URL` — default `https://api.telegram.org`, overridable for testing.

## Run with Docker

```sh
docker build -t broadcaster broadcaster
docker run --rm \
  -e NATS_URL=nats://... \
  -e TELEGRAM_BOT_TOKEN=... -e TELEGRAM_CHAT_ID=... \
  broadcaster
```

A failed Telegram call is logged and dropped: a missing chat message is
acceptable, a duplicate is not.
