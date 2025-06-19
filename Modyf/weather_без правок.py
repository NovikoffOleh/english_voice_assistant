import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=en"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    try:
        name = data['name']
        temp = round(data['main']['temp'])
        clouds = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        return (
            f"📍 {name}\n"
            f"🌡 Temperature: {temp}°C\n"
            f"☁️ Condition: {clouds}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬 Wind: {wind} m/s"
        )
    except:
        return None
