import json
from pydantic import BaseModel

from shared.llm.sarvam import sarvam_chat_completion
from shared.llm.gemini import gemini_image_generation


class StoryMetadata(BaseModel):
    title: str = ""
    description: str = ""
    tags: list[str] = []


METADATA_PROMPT = """
Write a compelling and relevant title and description for the following storyline. Write in {language} only. 

{storyline}

Output JSON:
```json
{
   "title": "<compelling title in hindi>",
  "description": <brief and direct description of the storyline>"
}
```
"""

IMAGE_PROMPT = """
You are a professional illustrator. You are given a story line, setting of the story & style of the story. You need to generate a illustration for the audio story.
The story line is: {storyline}
The setting of the story is: {setting}

Output should follow the following guidelines:
- The image should be a square image with 1:1 aspect ratio and 1024x1024 resolution.
- The image should be an painted illustration of the story.
- The image should be a high-quality image.
- The image should be a image of the story.
- The image should be a image of the setting of the story.
"""


async def generate_metadata_for_storyline(
    storyline: str,
    language: str,
) -> StoryMetadata:
    try:
        prompt = METADATA_PROMPT.replace("{language}", language).replace(
            "{storyline}", storyline
        )
        genOutput = await sarvam_chat_completion(prompt)

        genJSON = genOutput.replace("```json", "").replace("```", "").strip()
        genJSON = json.loads(genJSON)

        return StoryMetadata(
            title=genJSON.get("title", ""),
            description=genJSON.get("description", ""),
        )
    except Exception as e:
        print(e)
        return StoryMetadata()


async def generate_image_for_story(storyline: str, setting: str, save_file: str):
    try:
        prompt = IMAGE_PROMPT.format_map({"storyline": storyline, "setting": setting})
        genOutput = await gemini_image_generation(prompt)

        if genOutput is None:
            raise Exception("failed to generate image for story")

        with open(save_file, "wb") as fp:
            fp.write(genOutput)

        return save_file
    except Exception as e:
        print(e)
        return ""
