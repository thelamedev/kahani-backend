import aiohttp
import os
import base64

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

GEMINI_IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-2.0-flash-preview-image-generation",
)
GEMINI_IMAGE_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_IMAGE_MODEL}:streamGenerateContent?key={GEMINI_API_KEY}"


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


async def gemini_image_generation(prompt: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            GEMINI_IMAGE_ENDPOINT,
            json={
                "generationConfig": {
                    "responseModalities": ["IMAGE", "TEXT"],
                    "responseMimeType": "text/plain",
                },
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt,
                            }
                        ]
                    }
                ],
            },
        )

        if resp.status > 200:
            print(await resp.text())
            resp.raise_for_status()

        chunk = await resp.json()
        image_base64 = (
            chunk[0]
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("inlineData", {})
            .get("data", None)
        )

        if image_base64 is None:
            return None

        return base64.b64decode(image_base64)
