import asyncio

async def reminder_task(context, chat_id: int, task_text: str, interval_sec: int):
    try:
        await asyncio.sleep(interval_sec)

        # Тільки текстове повідомлення, щоб спрацював системний звук Telegram
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏰ REMINDER — time is up!"
        )

    except Exception as e:
        print(f"[ReminderTask Error] {str(e)}")

def schedule_reminder(context, chat_id: int, task_text: str, interval_sec: int):
    context.application.create_task(reminder_task(context, chat_id, task_text, interval_sec))
