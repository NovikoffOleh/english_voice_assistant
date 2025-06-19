import whisper
import os
import subprocess

# Load Whisper model once (small = good balance between speed and accuracy)
model = whisper.load_model("small")

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

def recognize_speech(ogg_file_path: str) -> str:
    """
    Recognizes English speech from an OGG file using Whisper.
    :param ogg_file_path: path to the .ogg file
    :return: recognized text or error message
    """
    wav_path = ogg_file_path.replace(".ogg", ".wav")

    try:
        convert_ogg_to_wav(ogg_file_path, wav_path)
        result = model.transcribe(wav_path, language="en")
        return result.get("text", "").strip()
    except Exception as e:
        return f"⚠️ Voice recognition failed: {str(e)}"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
