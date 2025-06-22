import os
import subprocess
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, "-ac", "1", "-ar", "16000", wav_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[FFmpeg] Conversion error: {e}")
        raise RuntimeError("Audio conversion failed")

async def recognize_speech(ogg_file_path: str, language: str = "en") -> str:
    """
    Recognizes speech from an OGG file using OpenAI Whisper API.
    :param ogg_file_path: path to the .ogg file
    :param language: language code (e.g., "en", "uk")
    :return: recognized text or error message
    """
    wav_path = ogg_file_path.replace(".ogg", ".wav")

    try:
        convert_ogg_to_wav(ogg_file_path, wav_path)
        with open(wav_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcript.get("text", "").strip()
    except Exception as e:
        print(f"[Whisper Error] {str(e)}")
        return f"⚠️ Voice recognition failed: {str(e)}"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
