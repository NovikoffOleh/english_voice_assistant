import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> str:
    if not API_KEY:
        return "⚠️ Weather API key not found."

    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric&lang=en"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        name = data.get("name", "Unknown location")
        temp = round(data["main"]["temp"])
        clouds = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return (
            f"📍 {name}\n"
            f"🌡 Temperature: {temp}°C\n"
            f"☁️ Condition: {clouds}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬 Wind: {wind} m/s"
        )

    except requests.exceptions.RequestException as e:
        return f"⚠️ Weather request failed: {e}"
    except (KeyError, IndexError, TypeError) as e:
        return f"⚠️ Error parsing weather data: {e}"
