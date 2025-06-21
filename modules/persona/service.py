import json

from shared.llm.gemini import gemini_chat_completion
from shared.utils import format_prompt

persona_prompt = """
Kahani is a multi-agentic system for creating immersive audio-only stories based on user prompts. 
You are the persona generator character. The story outline agent will provide you with the story outline and other parameters like characters , mood, tone , setting etc. 
Based on these inputs , you have to think creatively and detailed personas for each character. The persona should include all necessary info about that character like name ,age , gender , background , personality traits etc.
These output combined with story outline will be used by scrip_generator agent to generate the script with dialouges for each character.

Story Outline and Parameters:
{story_outline}
  

<generation_instructions>
<1>
Please strictly follow the characters given in the input. Don't remove or generate any new character and its persona.
</1>
<2>
Strictly follow the instructions given above.Don't give any other extra text content other than JSON output.
</2>
<3>
personality_trait parameter should not be too long. It should be concise enough to cover key traits of the character.
</3>
</generation_instructions>


OUTPUT FORMAT (if there are 3 characters) :
```json
{
    "character_1": {
        "name": "...",
        "age": "...",
        "gender": "...",
        "background": "...",
        "personality_traits": "...",
        "voice_config": {
            "speaker": "model_name", 
            "pitch": "pitch_value"
        }
    },
    ...
}
```
"""


async def generate_character_person(story_outline: dict) -> dict:
    prompt = format_prompt(
        persona_prompt,
        {
            "story_outline": json.dumps(story_outline, indent=2),
        },
    )

    resp = await gemini_chat_completion(prompt)

    persona = resp.replace("```json", "").replace("```", "").strip()
    try:
        persona = json.loads(persona)
    except Exception as e:
        print(e)

    return persona
