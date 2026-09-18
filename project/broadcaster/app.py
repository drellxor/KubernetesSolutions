"""Broadcaster: forwards todo events from NATS to a Telegram chat.

Set BROADCAST_TARGET=log to keep the messages in the log instead, which is
what staging does. The choice is explicit rather than inferred from missing
credentials, so a mistyped secret cannot quietly turn production into a
log-only deployment.
"""

import asyncio
import json
import logging
import os
import signal

import httpx
import nats

NATS_URL = os.getenv("NATS_URL", "nats://my-nats.nats.svc.cluster.local:4222")
NATS_SUBJECT = os.getenv("NATS_SUBJECT", "todos")
# Every replica joins the same queue group, so NATS hands each message to
# exactly one of them. That is what makes scaling up safe.
NATS_QUEUE_GROUP = os.getenv("NATS_QUEUE_GROUP", "broadcaster")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "https://api.telegram.org")

BROADCAST_TARGET = os.getenv("BROADCAST_TARGET", "telegram").lower()
VALID_TARGETS = ("telegram", "log")

TIMEOUT_SECONDS = 10

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger("broadcaster")


def describe(event: dict) -> str:
    """The chat message for a todo event."""
    todo = event.get("todo", "")
    if event.get("action") == "created":
        return f"A new todo was created: {todo}"

    state = "done" if event.get("done") else "not done"
    return f"A todo was marked {state}: {todo}"


async def send_to_telegram(client: httpx.AsyncClient, text: str) -> None:
    response = await client.post(
        f"{TELEGRAM_API_URL}/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
    )
    response.raise_for_status()


async def main() -> None:
    if BROADCAST_TARGET not in VALID_TARGETS:
        raise SystemExit(
            f"BROADCAST_TARGET must be one of {VALID_TARGETS}, got {BROADCAST_TARGET!r}"
        )

    if BROADCAST_TARGET == "telegram" and not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")

    logger.info("Broadcasting to %s", BROADCAST_TARGET)

    connection = await nats.connect(NATS_URL)
    logger.info("Connected to %s, subscribing to %r", NATS_URL, NATS_SUBJECT)

    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stopping.set)

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:

        async def handle(message) -> None:
            try:
                event = json.loads(message.data)
            except json.JSONDecodeError:
                logger.warning("Ignoring unreadable message: %r", message.data[:200])
                return

            text = describe(event)
            if BROADCAST_TARGET == "log":
                logger.info("Would send: %s", text)
                return

            try:
                await send_to_telegram(client, text)
            except httpx.HTTPError as error:
                logger.warning("Could not send to Telegram: %s", error)
                return

            logger.info("Sent: %s", text)

        await connection.subscribe(
            NATS_SUBJECT, queue=NATS_QUEUE_GROUP, cb=handle
        )
        await stopping.wait()

    logger.info("Shutting down")
    await connection.drain()


if __name__ == "__main__":
    asyncio.run(main())
