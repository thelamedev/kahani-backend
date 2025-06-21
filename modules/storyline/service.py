import json

from shared.llm.gemini import gemini_chat_completion
from shared.utils import format_prompt

storyline_prompt = """
Kahani is a multi-agentic system for creating immersive audio-only stories based on user prompts. 
You are the story outline agent.As a story outline agent your task is to generate a story outline for the given user prompt. 
You have to reason , analyse and understand the user intent and generate the outline accordingly.
The outline should be detailed and should cover the necessary aspects of the story like the plot , characters , theme , mood, tone etc. 

<generation_instructions>
<1>
The number of characters should be less than or equal to 4. Story with characters beyond this limit will be unacceptable.
</1>
<2>
The story and plot should be such that the story duration could be between 3-6 minutesThe outline should not be too long.
</2>
<3>
Strictly follow the instructions given above.Don't give any other extra text content other than JSON output.
</3>
<4>
For each character, provide a short description of their context and role in the story.
</4>
</generation_instructions>

USER INPUT:
{user_input}
 
Your output should be in JSON format with the following parameters of the story : 
OUTPUT FORMAT : 
```json
{
    "plot_outline": "...",
    "characters": [
        {
            "name": "...",
            "description": "<a short description of their context and role in the story>"
        },
    ...],
    "mood": "...",
    "tone": "...",
    "setting": "...",
    "conflict": "...",
    "resolution": "...",
    "style": "..."  
}
```
"""


async def generate_story_outline(user_input: str):
    prompt = format_prompt(
        storyline_prompt,
        {
            "user_input": user_input,
        },
    )
    storyline_text = await gemini_chat_completion(prompt)

    storyline = storyline_text.replace("```json", "").replace("```", "").strip()
    try:
        storyline = json.loads(storyline)
    except Exception as e:
        print(e)

    return storyline
