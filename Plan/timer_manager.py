import asyncio
from datetime import datetime
import pytz

async def reminder_task(context, chat_id: int, task_text: str, interval_sec: int):
    try:
        # Отримуємо таймзону з user_data
        user_data = context.chat_data.get(chat_id) or context.user_data
        tz_name = user_data.get("timezone", "UTC")
        user_tz = pytz.timezone(tz_name)

        # Визначаємо точний момент спрацювання
        target_time = datetime.now(user_tz) + asyncio.timedelta(seconds=interval_sec)
        await asyncio.sleep(interval_sec)

        # Форматуємо час у таймзоні користувача
        formatted_time = datetime.now(user_tz).strftime("%H:%M")

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"⏰ REMINDER — it's {formatted_time} in your timezone ({tz_name})!\n\n"
                f"📝 Task: {task_text}"
            )
        )

    except Exception as e:
        print(f"[ReminderTask Error] {str(e)}")

def schedule_reminder(context, chat_id: int, task_text: str, interval_sec: int):
    """
    Schedule a reminder task with the specified interval and text.
    """
    context.application.create_task(
        reminder_task(context, chat_id, task_text, interval_sec)
    )
