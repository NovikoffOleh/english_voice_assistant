import re
from datetime import datetime, timedelta
import pytz
from modules.timezone_utils import get_user_timezone_offset

DIGITS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

def parse_task_request(text: str) -> dict | None:
    """
    Parses phrases like: "remind me to drink water in 30 minutes"
    """
    text = text.lower().strip()

    hour_match = re.search(
        r"(in\s+)?(?P<hours>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(hour|hours?)",
        text
    )
    minute_match = re.search(
        r"(?P<minutes>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(min|minute|minutes?)",
        text
    )

    hours = 0
    minutes = 0

    if hour_match:
        val = hour_match.group("hours")
        hours = int(val) if val.isdigit() else DIGITS.get(val, 0)
        text = text.replace(hour_match.group(0), "", 1)

    if minute_match:
        val = minute_match.group("minutes")
        minutes = int(val) if val.isdigit() else DIGITS.get(val, 0)
        text = text.replace(minute_match.group(0), "", 1)

    if not (hours or minutes):
        return None

    interval = timedelta(hours=hours, minutes=minutes)
    task_text = re.sub(r"\b(in|remind( me)?|to|minutes?|hours?)\b", "", text)
    task_text = re.sub(r"\s+", " ", task_text).strip() or "reminder"

    return {
        "interval": interval,
        "task_text": task_text
    }

async def parse_absolute_time_request(text: str, user_id: int) -> dict | None:
    """
    Parses phrases like: "remind me at 19:30", "remind at 7.45"
    Returns target UTC time in ISO format.
    """
    text = text.lower().strip()
    match = re.search(r"(at\s*)?(\d{1,2})([:\.\-])?(\d{2})?", text)
    if not match:
        return None

    try:
        hour = int(match.group(2))
        minute = int(match.group(4)) if match.group(4) else 0
    except ValueError:
        return None

    # Отримуємо локальний час користувача
    user_offset = await get_user_timezone_offset(user_id)
    user_now = datetime.utcnow() + timedelta(hours=user_offset)
    user_target = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if user_target <= user_now:
        user_target += timedelta(days=1)

    # Конвертуємо в UTC
    target_utc = user_target - timedelta(hours=user_offset)
    target_iso = target_utc.isoformat()

    task_text = text.replace(match.group(0), "")
    task_text = re.sub(r"\b(remind( me)?|at|to|minutes?|hours?)\b", "", task_text)
    task_text = re.sub(r"\s+", " ", task_text).strip() or "reminder"

    return {
        "target_time_utc": target_iso,
        "task_text": task_text
    }
