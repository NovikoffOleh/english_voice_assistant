import json
import os
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

TIMEZONE_FILE = "data/user_timezones.json"

def save_user_timezone(user_id, lat, lon):
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=lat, lng=lon)
    if not timezone:
        timezone = "UTC"

    if os.path.exists(TIMEZONE_FILE):
        with open(TIMEZONE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[str(user_id)] = {
        "timezone": timezone,
        "lat": lat,
        "lon": lon
    }

    with open(TIMEZONE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_timezone(user_id):
    if os.path.exists(TIMEZONE_FILE):
        with open(TIMEZONE_FILE, "r") as f:
            data = json.load(f)
        user_data = data.get(str(user_id))
        if user_data:
            return user_data.get("timezone", "UTC")
    return "UTC"

def has_timezone_offset(user_id):
    if os.path.exists(TIMEZONE_FILE):
        with open(TIMEZONE_FILE, "r") as f:
            data = json.load(f)
        return str(user_id) in data
    return False

def get_user_timezone_offset(user_id):
    """
    Returns the timezone offset in hours as float.
    """
    timezone_str = get_user_timezone(user_id)
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        offset = now.utcoffset()
        return offset.total_seconds() / 3600 if offset else 0
    except Exception as e:
        print(f"[⚠️] Failed to get offset for user {user_id}: {e}")
        return 0

def set_user_timezone_offset(user_id, offset_hours):
    """
    Manually set the user's timezone offset in hours (float).
    """
    if os.path.exists(TIMEZONE_FILE):
        with open(TIMEZONE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    if str(user_id) not in data:
        data[str(user_id)] = {}

    data[str(user_id)]["manual_offset"] = offset_hours

    with open(TIMEZONE_FILE, "w") as f:
        json.dump(data, f, indent=2)
