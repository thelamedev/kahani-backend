import os
from aiohttp import ClientSession

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")


async def send_discord_webhook_message(message: str, username: str | None = None):
    if not DISCORD_WEBHOOK:
        raise Exception(
            "'DISCORD_WEBHOOK' not set in environment, ignoring webhook sending"
        )

    if not message:
        raise Exception("empty message for discord webhook")

    payload = {
        "content": message,
    }
    if username:
        payload["username"] = username

    async with ClientSession() as session:
        resp = await session.post(DISCORD_WEBHOOK, json=payload)
        resp.raise_for_status()
