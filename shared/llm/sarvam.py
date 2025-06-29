import aiohttp
import os

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
if not SARVAM_API_KEY:
    raise Exception("'SARVAM_API_KEY' not set in the environment")

SARVAM_MODEL = os.getenv("SARVAM_MODEL", "")
SARVAM_ENDPOINT = "https://api.sarvam.ai/v1/chat/completions"


async def sarvam_chat_completion(
    prompt: str,
    *,
    temperature: float = 1.0,
    max_tokens: int = 8192,
):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            SARVAM_ENDPOINT,
            headers={
                "api-subscription-key": SARVAM_API_KEY or "",
                "content-type": "application/json",
            },
            json={
                "model": "sarvam-m",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "content": prompt,
                        "role": "user",
                    },
                ],
            },
        )

        resp.raise_for_status()

        resp_json = await resp.json()

        resp_text = (
            resp_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        )

        return resp_text
