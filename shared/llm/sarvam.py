import aiohttp
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
if not SARVAM_API_KEY:
    raise Exception("'SARVAM_API_KEY' not set in the environment")

SARVAM_MODEL = os.getenv("SARVAM_MODEL", "")
SARVAM_ENDPOINT = ""


async def sarvam_chat_completion(prompt: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            SARVAM_ENDPOINT,
            json={},
        )

        resp.raise_for_status()

        resp_json = await resp.json()

        resp_text = (
            resp_json.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        return resp_text
