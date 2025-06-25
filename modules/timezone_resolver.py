import requests
from timezonefinder import TimezoneFinder

def get_timezone(city_name: str) -> str | None:


    """
    Визначає часовий пояс (timezone) за назвою міста.

    :param city_name: Назва міста (наприклад, 'London', 'New York', 'Kyiv')
    :return: Назва таймзони у форматі 'Europe/Kyiv', або None якщо не знайдено
    """
    try:
        # Використовуємо Nominatim API для пошуку координат міста
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "city": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "timezone-resolver-bot"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])

        # Визначаємо таймзону по координатах
        tf = TimezoneFinder()
        timezone = tf.timezone_at(lat=lat, lng=lon)

        return timezone

    except Exception as e:
        print(f"[TimezoneResolver Error] {e}")
        return None
