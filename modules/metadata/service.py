import json
from pydantic import BaseModel

from shared.llm.sarvam import sarvam_chat_completion


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
