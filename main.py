import uvicorn
import dotenv

from shared.utils import find_ffmpeg

dotenv.load_dotenv()

if __name__ == "__main__":
    ffmpeg_path = find_ffmpeg()
    print(f"Using ffmpeg at {ffmpeg_path}")
    uvicorn.run("api:app")
