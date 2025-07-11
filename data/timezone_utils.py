# data/timezone_utils.py

from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

user_timezones = {}  # Зберігає user_id -> timezone string, напр. 'Europe/Kyiv'

def set_user_timezone(user_id: int, latitude: float, longitude: float) -> str:
    """
    Визначає часову зону за координатами користувача та зберігає її.
    """
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    if timezone_str:
        user_timezones[user_id] = timezone_str
    return timezone_str

def get_user_timezone(user_id: int) -> str | None:
    """
    Повертає часову зону користувача, якщо вона була збережена.
    """
    return user_timezones.get(user_id)

def to_user_local_time(user_id: int, dt_utc: datetime) -> datetime | None:
    """
    Переводить час UTC у локальний час користувача.
    """
    timezone_str = get_user_timezone(user_id)
    if timezone_str:
        local_tz = pytz.timezone(timezone_str)
        return dt_utc.astimezone(local_tz)
    return None

def from_user_local_time(user_id: int, dt_local: datetime) -> datetime | None:
    """
    Переводить локальний час користувача у UTC.
    """
    timezone_str = get_user_timezone(user_id)
    if timezone_str:
        local_tz = pytz.timezone(timezone_str)
        return local_tz.localize(dt_local).astimezone(pytz.utc)
    return None
