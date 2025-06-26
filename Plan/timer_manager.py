import asyncio

async def reminder_task(context, chat_id: int, task_text: str, interval_sec: int):
    try:
        await asyncio.sleep(interval_sec)

        # Надсилання нагадування з текстом завдання
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ REMINDER — time is up!\n\n📝 Task completed"
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
