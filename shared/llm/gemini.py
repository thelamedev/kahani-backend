import aiohttp
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"


async def gemini_chat_completion(prompt: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            GEMINI_ENDPOINT,
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt,
                            }
                        ]
                    }
                ]
            },
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
