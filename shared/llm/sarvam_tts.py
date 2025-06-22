import os
import aiohttp
from dataclasses import dataclass

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
if not SARVAM_API_KEY:
    raise Exception("'SARVAM_API_KEY' not set in the environment")


@dataclass
class VoiceConfig:
    speaker: str

    # Range: -0.75 to 0.75
    pitch: float = 0.0
    # Range: 0.3 to 1
    pace: float = 0.9
    # Range: 0.1 to 3
    loudness: float = 1.0


async def generate_sarvam_voice(
    text: str,
    language: str,
    voice_config: VoiceConfig,
    session: aiohttp.ClientSession,
):
    resp = await session.post(
        url="https://api.sarvam.ai/text-to-speech",
        headers={
            "api-subscription-key": SARVAM_API_KEY or "",
            "content-type": "application/json",
        },
        json={
            "model": "bulbul:v2",
            "text": text,
            "target_language_code": language,
            "speaker": voice_config.speaker.lower(),
            "pitch": voice_config.pitch,
            "pace": voice_config.pace,
            "loudness": voice_config.loudness,
        },
    )

    if resp.status > 299:
        print(await resp.text())

    resp.raise_for_status()

    return await resp.json()


def rotate_sarvam_api_keys():
    return SARVAM_API_KEY
