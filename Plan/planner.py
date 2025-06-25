import re
from datetime import datetime, timedelta

# Для обробки відносних інтервалів
def parse_task_request(text: str) -> dict | None:
    text = text.lower().strip()

    digits = {
           "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
           "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    hour_match = re.search(
        
        r"(in\s+)?(?P<hours>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(hour|hours?)",
        text)
    minute_match = re.search(
       
        r"(?P<minutes>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(min|minute|minutes?)",
        text)

    hours = 0
    minutes = 0

    if hour_match:
        val = hour_match.group("hours")
        hours = int(val) if val.isdigit() else digits.get(val, 0)
        text = text.replace(hour_match.group(0), "", 1)

    if minute_match:
        val = minute_match.group("minutes")
        minutes = int(val) if val.isdigit() else digits.get(val, 0)
        text = text.replace(minute_match.group(0), "", 1)

    if not (hours or minutes):
        return None

    interval_sec = hours * 3600 + minutes * 60

    # 🔧 Повна очистка від "через", "нагадай", "хвилин" тощо
    cleaned_text = text
    cleaned_text = re.sub(r"\b(in|remind( me)?|to|minutes?|hours?)\b", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    task_text = cleaned_text if cleaned_text else "reminder"

    return {
        "interval_sec": interval_sec,
        "task_text": task_text
    }

# Для обробки абсолютного часу
def parse_absolute_time_request(text: str) -> dict | None:
    text = text.lower().strip()

    match = re.search(r"(at\s*)?(\d{1,2})([:\.\-])?(\d{2})?", text)
    if not match:
        return None

    try:
        hour = int(match.group(2))
        minute = int(match.group(4)) if match.group(4) else 0
    except ValueError:
        return None

    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_time <= now:
        target_time += timedelta(days=1)

    interval_sec = int((target_time - now).total_seconds())

    task_text = text.replace(match.group(0), "").replace("remind", "")
    #task_text = re.sub(r"\b(at|хв(илин(у)?)?|год(ин(у)?)?)\b", "", task_text)
    task_text = re.sub(r"\s+", " ", task_text).strip()
    task_text = task_text if task_text else "reminder"

    return {
        "interval_sec": interval_sec,
        "task_text": task_text
    }
