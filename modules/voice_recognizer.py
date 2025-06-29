import os
import subprocess
from faster_whisper import WhisperModel

# Завантажуємо модель один раз при старті
model_size = "small"  # можна "tiny", "base", "small", "medium", "large"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

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
    Recognizes speech from an OGG file using faster-whisper.
    :param ogg_file_path: path to the .ogg file
    :param language: language code ("en", "uk", etc.)
    :return: recognized text or error message
    """
    wav_path = ogg_file_path.replace(".ogg", ".wav")

    try:
        convert_ogg_to_wav(ogg_file_path, wav_path)

        segments, info = model.transcribe(wav_path, language=language)
        full_text = " ".join([segment.text for segment in segments])
        return full_text.strip()

    except Exception as e:
        print(f"[faster-whisper Error] {str(e)}")
        return f"⚠️ Voice recognition failed: {str(e)}"
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
