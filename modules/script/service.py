import json

from shared.llm.gemini import gemini_chat_completion
from shared.utils import format_prompt

script_prompt = """
Kahani is a multi-agentic platform for creating immersive audio-only stories based on user prompts.
You are the Script generator prompt. Story outline agent and persona generator agent will provide you with the story outline and persona of each character.
Based on these inputs , you have to think creatively and generate script for the whole story having dialogues for each character.The dialogues should feel natural and not robotic. 
The dialogues should be in the form of JSON. The dialogues should be sequenced in such a way that the story flow is immersive and continuous.
The script should be written such that it covers the story and duration is around 10 minutes.
 
<generation_instructions>
<1> Please strictly follow the  story outline and persona given in the input. Don't remove or generate any new character and its dialogues. </1>
<2> The script should strictly stick to the story outline ,plot and the characters.It should not go out of the context.  </2>
<3> Strictly follow the instructions given above.Don't give any other extra text content other than JSON output. </3>
<4> Based on character persona and and story, give a voice to each character in the script. the voice model options are given in voice_model_parameters.Accordingly select the voice model for each character. </4>
<5> All speaker text should be in {language}. Use the appropriate writing script for {language} when generating speaker text. </5>
<6> Based on script dialogues and demand for the story, set the voice parameters for each character in the script The parameters are pitch , pace and loudness. these parameters might be different for the same character too at different points of time in the script.
You have to think carefully and set the parameters accordingly to make the audio more immersive and engaging. The parameters and their respective value ranges are given in voice_parameters. 

"voice_parameters": {
    "pace" : "[0.5 , 1]",
    "loudness" : "[-0.3 , 3]"
}

Default values for pace is 1 and loudness is 1. Use these defaults to adjust your loudness and pitch in the dialogues.
</6>
<7> The number of dialogues and length of script should be according to duration of the story mentioned above.</7>

</generation_instructions>

<important_instruction>
General rule of thumb to be followed while designing dialogues for the script.
- If duration mentioned is 10 minutes , the script should have 120-130 dialogues
- if the duration mentioned is around 5 minutes , the script should have around 100 dialogues.
- If it is 2.5-3 minutes , the script should have  around 30-35 dialogues.
- Strictly follow this rule.Otherwise the story won't be acceptable.
</important_instruction>

Story Outline:
{story_outline}


Character Person:
{persona}


OUTPUT FORMAT for script dialogues:
```json
[
    {"speaker": "narrator", "text": "It was a stormy night…" , voice_config : { "pace" : "pace_value" , "loudness" : "loudness_value"}} ,
    {"speaker": "character1", "text": "Do you hear that?" , voice_config : { "pace" : "pace_value" , "loudness" : "loudness_value"}} ,
    ...
    {"speaker" : "character2" , "text" : "dialogue for character2" , "voice_config" : { "pace" : "pace_value" , "loudness" : "loudness_value"}} ,
    {"speaker" : "character3" , "text" : "dialogue for character3" , "voice_config" : { "pace" : "pace_value" , "loudness" : "loudness_value"}}  
]
```
"""


async def generate_script(story_outline: dict, persona: dict, language: str) -> dict:
    prompt = format_prompt(
        script_prompt,
        {
            "story_outline": json.dumps(story_outline, indent=2),
            "persona": json.dumps(persona, indent=2),
            "language": language,
        },
    )

    resp = await gemini_chat_completion(prompt)

    script = resp.replace("```json", "").replace("```", "").strip()
    try:
        script = json.loads(script)
    except Exception as e:
        print(e)

    return script
