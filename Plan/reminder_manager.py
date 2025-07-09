import json
import asyncio
from datetime import datetime
from telegram import Bot

REMINDER_FILE = "data/reminders.json"


async def load_reminders():
    try:
        with open(REMINDER_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


async def add_reminder(user_id, task_text, target_time_str):
    reminders = await load_reminders()

    if str(user_id) not in reminders:
        reminders[str(user_id)] = []

    reminders[str(user_id)].append({
        "time": target_time_str,
        "task": task_text
    })

    await save_reminders(reminders)


async def check_and_send_reminders(bot: Bot):
    while True:
        now = datetime.now()
        reminders = await load_reminders()
        updated = False

        for user_id, user_reminders in list(reminders.items()):
            to_send = []

            for reminder in user_reminders:
                try:
                    target_time = datetime.fromisoformat(reminder["time"])
                    if now >= target_time:
                        to_send.append(reminder)
                except Exception:
                    continue

            for reminder in to_send:
                await bot.send_message(chat_id=int(user_id), text=f"⏰ Reminder: {reminder['task']}")
                user_reminders.remove(reminder)
                updated = True

        if updated:
            await save_reminders(reminders)

        await asyncio.sleep(30)  # перевірка кожні 30 секунд
from telegram.ext import Application

def start_reminder_checker(application: Application):
    bot = application.bot
    application.create_task(check_and_send_reminders(bot))
