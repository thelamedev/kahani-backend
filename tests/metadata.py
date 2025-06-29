import asyncio
from modules.metadata.service import generate_metadata_for_storyline


async def test_metadata_generation():
    language = "hindi"
    storyline = "The story begins with Sita expressing her admiration for a beautiful golden deer to Rama. Entranced by its beauty, she pleads with Rama to capture it for her. Despite Lakshmana's warnings about the deer potentially being a demon in disguise, Rama, driven by his love for Sita, decides to pursue the deer. Before leaving, Rama instructs Lakshmana to protect Sita at all costs. As Rama chases the deer deeper into the forest, it leads him on a wild goose chase, exhausting him. Eventually, Rama realizes that the deer is indeed a demon, and he shoots it with an arrow. As the deer dies, it cries out in Rama's voice, 'Lakshmana, save me!' Sita overhears the cry and urges Lakshmana to go to Rama's aid. Lakshmana, bound by Rama's orders to protect Sita, initially refuses, explaining that Rama is invincible. However, Sita accuses him of wanting Rama dead so he can have her. Overwhelmed by Sita's accusations and fearing for Rama's safety, Lakshmana reluctantly agrees to go search for Rama. Before leaving, he draws a protective line (the Lakshman Rekha) around the hut, instructing Sita not to cross it under any circumstances. Ravana, disguised as a mendicant, approaches Sita and asks for alms. Remembering Lakshmana's warning, Sita offers him alms from beyond the line. Ravana insists that she come closer, but Sita refuses to cross the Lakshman Rekha. Ravana then reveals his true form and abducts Sita, carrying her away in his flying chariot."

    metadata = await generate_metadata_for_storyline(storyline, language)

    print(metadata)


if __name__ == "__main__":
    asyncio.run(test_metadata_generation())
