import aiohttp
import os
from dotenv import load_dotenv

# Завантаження .env
load_dotenv()

# Отримання ключа
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Діагностика: показати стан ключа
if OPENAI_API_KEY is None:
    print("❌ OPENAI_API_KEY not found! Check your .env file.")
else:
    print("✅ OPENAI_API_KEY loaded. First 10 chars:", OPENAI_API_KEY[:10])


async def recognize_with_openai(audio_path: str, language: str = "en") -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # Перевірка перед запитом
    if OPENAI_API_KEY is None:
        return "❌ API key missing. Cannot perform speech recognition."

    async with aiohttp.ClientSession() as session:
        with open(audio_path, "rb") as audio_file:
            data = aiohttp.FormData()
            data.add_field('file', audio_file, filename="audio.ogg", content_type='audio/ogg')
            data.add_field('model', 'whisper-1')
            data.add_field('language', language)  # ✅ Додано підтримку параметра language

            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("text", "")
                else:
                    error_text = await resp.text()
                    print(f"[Whisper API Error] {error_text}")
                    return "⚠️ Could not recognize the speech. Try again."
