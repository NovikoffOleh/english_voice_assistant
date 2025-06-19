import os
import re
import asyncio
import nest_asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from modules.voice_recognizer import recognize_speech
from modules.gpt_handler import ask_gpt
from modules.image_search import get_image_url
from cinema.movie_search import search_movie, get_top_movies, get_top_by_genre
from modules.weather import get_weather
from Plan.planner import parse_task_request, parse_absolute_time_request
from Plan.timer_manager import schedule_reminder
from modules.mood_checker import send_mood_request, handle_mood_callback
from modules.news_fetcher import fetch_news  # <--- ДОДАНО

nest_asyncio.apply()

load_dotenv()
TOKEN = os.getenv("TOKEN")

GENRE_MAP = {
    "тріллер": 53,
    "детектив": 9648,
    "фантастика": 878,
    "бойовик": 28,
    "комедія": 35,
    "хорор": 27,
    "фентезі": 14,
    "дитяче кіно": 16,
    "мелодрама": 10749,
    "історичний": 36,
    "музичний": 10402,
    "катастрофа": 12
}

def clean_query(text):
    stopwords = ["image", "download", "picture"]
    words = text.lower().split()
    filtered = [word for word in words if word not in stopwords]
    cleaned = " ".join(filtered)
    return re.sub(r"[^\w\s]", "", cleaned)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    keyboard = [
        
        ["💬 Queries", "🎮 Movies"],
        ["🗓 Plan", "🧘 Relax"],
        ["🌤 Weather", "🗞 News"],
        ["ℹ️ Help", "🌐 Language"]
    ]

    now = datetime.now().hour
    if 5 <= now < 12:
        greeting_time = "🌅 Good morning"
    elif 12 <= now < 18:
        greeting_time = "🌞 Good afternoon"
    elif 18 <= now < 22:
        greeting_time = "🌇 Good evening"
    else:
        greeting_time = "🌙 Good night"

    if name:
        greeting = (
            f"{greeting_time}\n"
            f"{name}!\n"
            "I'm LUMO – your personal assistant for all things.\n"
            "I can answer questions, search images, set reminders and help you plan your day.\n"
            "Say or type: 'Show me a cat', 'Remind me in 5 minutes to take my medicine'.\n"
            "All commands: /help"
            )
            await update.message.reply_text(greeting, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        else:
            await update.message.reply_text(f"{greeting_time}! 🤓 What is your name?")
            context.user_data["awaiting_name"] = True
    

async def cinema_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔍 Шукати кіно"],
        ["⭐ Рейтингове кіно"],
        ["🎲 Запропонувати кіно"],
        ["🔙 Головне меню"]
    ]
    name = context.user_data.get("name", "друже")
    await update.message.reply_text(f"🍿 {name}, обери дію:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name", "друже")
    help_text = (
        f"⚙️ {name}, ось що я вмію:\n"
        "/plan — нагадування або строкові завдання\n"
        "/cinema — знайти фільм\n"
        "/relax — емоційне розвантаження\n"
        "/lang — вибір мови\n"
        "/gpt — режим запитів\n"
        "/help — довідка\n"
        "⚠️ — завдання з часовими приміжками типу 'нагадай 20:45(20.45) включити ТВ', вводяться тільки вручну\n"
        "⚠️ — назви фільмів, вводяться англійською і тільки вручну\n"
        "⚠️ — бот приймає терміновані завдання на добу\n"
    )
    await update.message.reply_text(help_text)

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_task"] = True
    name = context.user_data.get("name", "друже")
    await update.message.reply_text(f"📝  {name}, що будемо планувати?Наприклад: 'Нагадай через 10 хвилин про зустріч'")

async def gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_task"] = False
    name = context.user_data.get("name", "друже")
    await update.message.reply_text(f"🔄  {name}, режим запитів активовано — можеш ставити питання або шукати зображення.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.voice:
            file = await context.bot.get_file(update.message.voice.file_id)
            voice_path = f"data/{update.message.voice.file_id}.ogg"
            await file.download_to_drive(voice_path)
            await update.message.reply_text("🎧 Розпізнаю мову...")
            try:
                recognized_text = recognize_speech(voice_path)
                recognized_text = re.sub(r"[^\w\s]", "", recognized_text).lower().strip()
                await update.message.reply_text(f"💤 {context.user_data.get('name', 'друже')}, ти сказав: {recognized_text}")
                await process_text(update, context, recognized_text)
            finally:
                if os.path.exists(voice_path):
                    os.remove(voice_path)
        elif update.message.text:
            text = update.message.text.lower().strip()
            await process_text(update, context, text)
        else:
            await update.message.reply_text("⚠️ Тип повідомлення не підтримується.")
    except Exception as e:
        print(f"[Main Error] {e}")
        await update.message.reply_text("⚠️ Сталася технічна помилка. Спробуйте ще раз пізніше.")

#
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.voice:
            file = await context.bot.get_file(update.message.voice.file_id)
            voice_path = f"data/{update.message.voice.file_id}.ogg"
            await file.download_to_drive(voice_path)
            await update.message.reply_text("🎧 Розпізнаю мову...")
            try:
                recognized_text = recognize_speech(voice_path)
                recognized_text = re.sub(r"[^\w\s]", "", recognized_text).lower().strip()
                # Перевірка sleep-mode для голосових
                if context.user_data.get("sleep_mode") and recognized_text not in ["привіт", "/start", "почати"]:
                    await update.message.reply_text("😴 Я зараз у сплячому режимі. Напиши 'Привіт' або /start, щоб активувати мене.")
                    return
                if any(phrase in recognized_text for phrase in ["до побачення", "до зустрічі", "прощавай", "па-па", "бувай", "bye", "goodbye", "see you"]):
                    context.user_data["sleep_mode"] = True
                    await update.message.reply_text("🛌 Переходжу у сплячий режим. Активуюсь при новому зверненні.")
                    return
                if context.user_data.get("sleep_mode") and recognized_text in ["привіт", "/start", "почати"]:
                    context.user_data["sleep_mode"] = False
                    await update.message.reply_text("👋 Я знову на звʼязку!")
                await process_text(update, context, recognized_text)
            finally:
                if os.path.exists(voice_path):
                    os.remove(voice_path)
        elif update.message.text:
            text = update.message.text.lower().strip()
            if context.user_data.get("sleep_mode") and text not in ["привіт", "/start", "почати"]:
                await update.message.reply_text("😴 Я зараз у сплячому режимі. Напиши 'Привіт' або /start, щоб активувати мене.")
                return
            if any(phrase in text for phrase in ["до побачення", "до зустрічі", "прощавай", "па-па", "бувай", "bye", "goodbye", "see you"]):
                context.user_data["sleep_mode"] = True
                await update.message.reply_text("🛌 Переходжу у сплячий режим. Активуюсь при новому зверненні.")
                return
            if context.user_data.get("sleep_mode") and text in ["привіт", "/start", "почати"]:
                context.user_data["sleep_mode"] = False
                await update.message.reply_text("👋 Я знову на звʼязку!")
            await process_text(update, context, text)
        else:
            await update.message.reply_text("⚠️ Тип повідомлення не підтримується.")
    except Exception as e:
        print(f"[Main Error] {e}")
        await update.message.reply_text("⚠️ Сталася технічна помилка. Спробуйте ще раз пізніше.")
#
async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):

    if context.user_data.get("awaiting_name"):
        context.user_data["name"] = text.title()
        context.user_data["awaiting_name"] = False
        await update.message.reply_text(f"Приємно познайомитись, {context.user_data['name']} 😊")
        await start(update, context)
        return

    if text == "🌤 прогноз погоди":
        context.user_data["awaiting_city"] = True
        name = context.user_data.get("name", "друже")
        await update.message.reply_text("📍Вкажи місто, для якого дізнатися прогноз:")
        return
        
    if text == "🗞 новини":
        await update.message.reply_text("📡 Завантажую останні новини...")
        news_list = fetch_news(language="uk", limit=4)
        for item in news_list:
            await update.message.reply_text(item)
        return

    if context.user_data.get("awaiting_city"):
        context.user_data["awaiting_city"] = False
        forecast = get_weather(text)
        if forecast:
            await update.message.reply_text(forecast)
        else:
            await update.message.reply_text("⚠️ Не вдалося знайти місто або отримати прогноз. Спробуйте ще раз.")
        return

    trigger_words = ["покажи", "завантаж", "фото", "зображення", "image", "download", "picture"]

    if text in ["/cinema", "кіно", "дивитися", "🎮 кіно"]:
        await cinema_command(update, context)
        return

    if text == "🔍 шукати кіно":
        context.user_data["awaiting_movie_title"] = True
        await update.message.reply_text("🎬 Введи назву фільму англійською мовою")
        return

    if context.user_data.get("awaiting_movie_title"):
        context.user_data["awaiting_movie_title"] = False
        movie = search_movie(text)
        if movie is None:
            await update.message.reply_text("⚠️ Такого фільму не знайдено.")
        elif "error" in movie:
            await update.message.reply_text(f"⚠️ Помилка: {movie['error']}")
        else:
            reply = (
                f"🎬 Назва: {movie['title']} ({movie['year']})\n"
                f"⭐ IMDb: {movie['rating']}\n"
                f"📝 Сюжет: {movie['plot']}\n"
                f"🔗 Дивитися: {movie['imdb_link']}"
            )
            if movie['poster'] and movie['poster'] != "N/A":
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["🔍 Шукати кіно", "🎮 Кіно"], ["🔙 Головне меню"]]
        await update.message.reply_text("📽 Обери наступну дію:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "⭐ рейтингове кіно":
        await update.message.reply_text("📊 Завантажую топ фільмів...")
        movies = get_top_movies()
        if not movies:
            await update.message.reply_text("⚠️ Не вдалося отримати список фільмів.")
            return
        for movie in movies:
            reply = (
                f"🎬 {movie['title']} ({movie['year']})\n"
                f"⭐ Рейтинг: {movie['rating']}\n"
                f"📝 {movie['plot']}\n"
                f"🔗 {movie['link']}"
            )
            if movie['poster']:
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["⭐ Рейтингове кіно", "🎮 Кіно"], ["🔙 Головне меню"]]
        await update.message.reply_text("📽 Обери наступну дію:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "🎲 запропонувати кіно":
        keyboard = [
            ["Тріллер", "Детектив", "Фантастика"],
            ["Бойовик", "Комедія", "Хорор"],
            ["Фентезі", "Дитяче кіно", "Мелодрама"],
            ["Історичний", "Музичний", "Катастрофа"],
            ["🔙 Головне меню"]
        ]
        await update.message.reply_text("🎬 Обери жанр:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text.lower() in GENRE_MAP:
        genre_id = GENRE_MAP[text.lower()]
        await update.message.reply_text(f"🎞 Пошук фільмів у жанрі: {text.title()}...")
        movies = get_top_by_genre(genre_id)
        if not movies:
            await update.message.reply_text("⚠️ Не вдалося знайти фільми за цим жанром.")
            return
        for movie in movies:
            reply = (
                f"🎬 {movie['title']} ({movie['year']})\n"
                f"⭐ Рейтинг: {movie['rating']}\n"
                f"📝 {movie['plot']}\n"
                f"🔗 {movie['link']}"
            )
            if movie['poster']:
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["🎲 Запропонувати кіно", "🎮 Кіно"], ["🔙 Головне меню"]]
        await update.message.reply_text("🎯 Обери наступну дію:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "🧘 релакс":
        keyboard = [["🌧 Дощ", "🔥 Камін", "🎵 Релакс"], ["🔙 Головне меню"]]
        await update.message.reply_text("🧘 Обери режим релаксу:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text in ["🌧 дощ", "🔥 камін", "🎵 релакс"]:
        sounds = {
            "🌧 дощ": "https://www.youtube.com/watch?v=GxE6g1fLxoo",
            "🔥 камін": "https://www.youtube.com/watch?v=eyU3bRy2x44",
            "🎵 релакс": "https://www.youtube.com/watch?v=2OEL4P1Rz04"
        }
        await update.message.reply_text(f"🎧 Насолоджуйся релаксом: {sounds[text]}")
        return

    if text == "🔙 головне меню":
        await start(update, context)
        return

    if text in ["ℹ️ допомога", "/help"]:
        await help_command(update, context)
        return

    if text in ["запити", "/gpt", "💬 запити"]:
        await gpt_mode(update, context)
        return

    if text in ["завдання", "/plan", "план", "🗓 план"]:
        context.user_data["awaiting_task"] = True
        await update.message.reply_text("📝 Що саме будемо планувати? Наприклад: 'Нагадай через 10 хвилин про зустріч'")
        return

    if context.user_data.get("awaiting_task"):
        context.user_data["awaiting_task"] = False
        parsed = parse_task_request(text)
        if parsed:
            task_text = parsed["task_text"].replace("нагадай", "", 1).strip()
            schedule_reminder(context, update.effective_chat.id, task_text, parsed["interval_sec"])
            await update.message.reply_text(f"✅ Нагадування прийняте\n⏳ Потурбую тебе через {parsed['interval_sec'] // 60} хв")
            return
        parsed_abs = parse_absolute_time_request(text)
        if parsed_abs:
            task_text = parsed_abs["task_text"].replace("нагадай", "", 1).strip()
            schedule_reminder(context, update.effective_chat.id, task_text, parsed_abs["interval_sec"])
            await update.message.reply_text(f"✅ Нагадування прийняте\n🕒 Спрацює о вказаній годині")
            return
        await update.message.reply_text("⚠️ Не вдалося розпізнати час. Спробуйте ще раз.")
        return

    if any(trigger in text for trigger in trigger_words):
        query = clean_query(text)
        await update.message.reply_text("🔍 Шукаю зображення...")
        result = get_image_url(query)
        if result.startswith("http"):
            await update.message.reply_photo(result)
        else:
            await update.message.reply_text(result)
        return

    await update.message.reply_text("🧠 Обробляю через GPT...")
    gpt_reply = ask_gpt(text)
    try:
        await update.message.reply_text(gpt_reply)
    except:
        await update.message.reply_text("⚠️ Відповідь GPT не вдалося відобразити.")

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from modules.mood_checker import send_mood_request, handle_mood_callback

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("cinema", cinema_command))
    app.add_handler(CommandHandler("gpt", gpt_mode))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
    app.add_handler(CallbackQueryHandler(handle_mood_callback, pattern=r"^mood_"))

    # 🧠 Функція обгортка для async-виклику настрою
    async def run_send_mood():
        await send_mood_request(app)

    # ⏰ Планувальник
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_send_mood, CronTrigger(hour=8, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=12, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=16, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=20, minute=0))  # тест
    scheduler.start()

    print("🟢 Bot is running. Open Telegram and type /start")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())




