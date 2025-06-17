import whisper
import os
import subprocess

# Завантаження моделі (більш точна ніж "tiny")
model = whisper.load_model("small")

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    # Конвертація у WAV: моно 16 kHz для стабільності розпізнавання
    subprocess.run([
        "ffmpeg", "-y", "-i", ogg_path,
        "-ac", "1",        # моно
        "-ar", "16000",     # 16 kHz
        wav_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def recognize_speech(ogg_file_path: str) -> str:
    wav_path = ogg_file_path.replace(".ogg", ".wav")
    convert_ogg_to_wav(ogg_file_path, wav_path)

    # Використання Whisper з фіксованою українською мовою
    result = model.transcribe(wav_path, language="uk")

    os.remove(wav_path)  # очищення після обробки
    return result["text"]
