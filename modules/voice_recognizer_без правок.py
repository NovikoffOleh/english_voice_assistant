import whisper
import os
import subprocess

# Load the more accurate model (better than "tiny")
model = whisper.load_model("small")

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    # Convert to WAV: mono 16 kHz for better recognition stability
    subprocess.run([
        "ffmpeg", "-y", "-i", ogg_path,
        "-ac", "1",        # mono
        "-ar", "16000",    # 16 kHz
        wav_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def recognize_speech(ogg_file_path: str) -> str:
    """
    Recognizes English speech from an OGG file.
    :param ogg_file_path: path to the .ogg file
    :return: recognized text
    """
    wav_path = ogg_file_path.replace(".ogg", ".wav")
    convert_ogg_to_wav(ogg_file_path, wav_path)

    # Whisper: force English language recognition
    result = model.transcribe(wav_path, language="en")

    os.remove(wav_path)  # cleanup after processing
    return result["text"]
