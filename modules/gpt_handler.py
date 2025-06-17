import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-8b-8192"  # or "mistral-7b-8k"

def ask_gpt(prompt: str) -> str:
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a smart, friendly English-speaking personal assistant. "
                        "You help users with everything — from healthy eating and daily planning to finding content and solving math problems. "
                        "You respond shortly, with wit and positivity. If asked about a famous person or uncertain event — do not invent facts. "
                        "Instead, reply: 'This information needs further verification.'"
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 512
        }

        response = requests.post(url, headers=headers, json=payload, timeout=20)

        if response.status_code != 200:
            return f"⚠️ Groq GPT error: {response.status_code}\n{response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"⚠️ GPT unavailable: {str(e)}"

def get_motivation() -> str:
    styles = [
        "Say something inspiring to start the day.",
        "Say a motivational quote for a beginner entrepreneur.",
        "Say a short funny motivational message to lift someone's mood."
    ]
    return ask_gpt(random.choice(styles))
