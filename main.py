import os
import uvicorn
import dotenv

from shared.utils import find_ffmpeg

dotenv.load_dotenv()

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", "8000"))

    ffmpeg_path = find_ffmpeg()
    print(f"Using ffmpeg at {ffmpeg_path}")
    uvicorn.run("api:app", port=PORT)
