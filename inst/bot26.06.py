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
from modules.news_fetcher import fetch_news  # &lt;--- ADDED
from modules.timezone_resolver import get_timezone
from pytz import timezone as pytz_timezone
import pytz


nest_asyncio.apply()
load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = os.getenv("KMP_DUPLICATE_LIB_OK", "FALSE")

TOKEN = os.getenv("TOKEN")

GENRE_MAP = {
    "thriller": 53,
    "detective": 9648,
    "sci-fi": 878,
    "action": 28,
    "comedy": 35,
    "horror": 27,
    "fantasy": 14,
    "family": 16,
    "romance": 10749,
    "history": 36,
    "musical": 10402,
    "disaster": 12
}

def clean_query(text):
    stopwords = ["show", "upload", "photo", "image", "download", "picture"]
    words = text.lower().split()
    filtered = [word for word in words if word not in stopwords]
    cleaned = " ".join(filtered)
    return re.sub(r"[^\w\s]", "", cleaned)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    timezone_str = context.user_data.get("timezone")

    keyboard = [
        ["💬 Queries", "🎮 Movies"],
        ["🗓 Plan", "🧘 Relax"],
        ["🌤 Weather Forecast", "🗞 News"],
        ["ℹ️ Help"]
    ]

    # Визначаємо локальний час, якщо timezone є
    if timezone_str:
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz).hour
        except Exception as e:
            print(f"[start] Timezone error: {e}")
            now = datetime.now().hour
    else:
        now = datetime.now().hour

    # Привітання по часу
    if 5 <= now < 12:
        greeting_time = "🌅 Good morning"
    elif 12 <= now < 18:
        greeting_time = "🌞 Good afternoon"
    elif 18 <= now < 22:
        greeting_time = "🌇 Good evening"
    else:
        greeting_time = "🌙 Good night"

    # Якщо ім'я є – показує головне меню
    if name and timezone_str:
        greeting = (
            f"{greeting_time}, {name}!\n"
            "I am LUMO - your personal assistant for all your needs.\n"
            "I can answer queries, find photos, remind you of appointments, and plan your day.\n"
            "Just say or type: 'Show me a cat', 'Remind me to take my medicine in 5 minutes', and I'll do it.\n"
            "All commands: /help"
        )
        await update.message.reply_text(greeting, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # Якщо ім'я є, але немає timezone → запитуємо місто
    elif name and not timezone_str:
        await update.message.reply_text(f"📍 {name}, to personalize my schedule, please tell me your city (e.g., London, Kyiv):")
        context.user_data["awaiting_city"] = True

    # Якщо ще немає імені → запитуємо ім’я
    else:
        await update.message.reply_text(f"{greeting_time}! 🤓 What is your name?")
        context.user_data["awaiting_name"] = True


async def cinema_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔍 Search for a movie"],
        ["⭐ Top Rated Movies"],
        ["🎲 Suggest a movie"],
        ["🔙 Main Menu"]
    ]
    name = context.user_data.get("name", "friend")
    await update.message.reply_text(f"🍿 {name}, choose an action:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name", "friend")
    help_text = (
        f"⚙️ {name}, here’s what I can do:\n"
        "/plan — reminders or urgent tasks\n"
        "/cinema — find a movie\n"
        "/relax — emotional relaxation\n"
        "/news — news for the hour\n"
        "/gpt — query mode\n"
        "/help — help\n"
        "⚠️ — tasks with time intervals like 'remind me at 8:45 PM to turn on the TV' can only be entered manually\n"
        "⚠️ — movie titles must be entered in English and only manually\n"
        "⚠️ — the bot accepts urgent tasks for one day\n"
    )
    await update.message.reply_text(help_text)

async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_task"] = True
    name = context.user_data.get("name", "friend")
    await update.message.reply_text(f"📝  {name}, what shall we plan? For example: 'Remind me in 10 minutes about the meeting'")

async def gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_task"] = False
    name = context.user_data.get("name", "friend")
    await update.message.reply_text(f"🔄  {name}, query mode is activated — you can ask questions or search for images.")

from modules.timezone_resolver import get_timezone

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    # Введення імені
    if context.user_data.get("awaiting_name"):
        context.user_data["name"] = text
        context.user_data["awaiting_name"] = False
        await update.message.reply_text(f"Nice to meet you, {text} 😊")
        await update.message.reply_text(f"📍 {text}, to personalize my schedule, please tell me your city (e.g., London, Kyiv):")
        context.user_data["awaiting_city"] = True
        return

    # Введення міста
    if context.user_data.get("awaiting_city"):
        context.user_data["city"] = text
        context.user_data["awaiting_city"] = False
        context.user_data["timezone"] = text  # Поки так — потім підключимо реальну timezone по API
        weather = await get_weather(text)
        if weather:
            await update.message.reply_text(weather)
        await start(update, context)
        return

    # Планування
    if "remind" in text.lower() or "meeting" in text.lower():
        result = parse_absolute_time_request(text)
        if result:
            task_text, scheduled_time = result
            schedule_reminder(context, chat_id, task_text, scheduled_time)
            await update.message.reply_text(f"✅ Reminder set for: {task_text} at {scheduled_time.strftime('%H:%M')}")
            return
        else:
            result = parse_task_request(text)
            if result:
                task_text, delay = result
                schedule_reminder(context, chat_id, task_text, datetime.now() + delay)
                await update.message.reply_text(f"✅ Reminder will be in {delay.seconds // 60} minutes")
                return

    # Окремий запит до погоди
    if "weather" in text.lower():
        city = context.user_data.get("city", "Kyiv")
        weather = await get_weather(city)
        if weather:
            await update.message.reply_text(weather)
            return

    # Запит до GPT
    if "?" in text or text.endswith("."):
        name = context.user_data.get("name", "")
        reply = ask_gpt(text)
        await update.message.reply_text(reply)
        return

    # Інакше — ввічлива відповідь
    await update.message.reply_text("🤔 I didn't understand. Try again or type /help.")



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.voice:
           file = await context.bot.get_file(update.message.voice.file_id)
           voice_path = f"data/{update.message.voice.file_id}.ogg"
           await file.download_to_drive(voice_path)
           await update.message.reply_text("🎧 Recognizing speech...")
           try:
               lang = context.user_data.get("lang", "en")
               recognized_text = await recognize_speech(voice_path, language=lang)
               #recognized_text = await recognize_with_faster_whisper(voice_path, language=lang)

               recognized_text = re.sub(r"[^\w\s]", "", recognized_text).lower().strip()
               await update.message.reply_text(f"💤 {context.user_data.get('name', 'friend')}, you said: {recognized_text}")
               await process_text(update, context, recognized_text)
           finally:
               if os.path.exists(voice_path):
                   os.remove(voice_path)
                

        elif update.message.text:
            text = update.message.text.lower().strip()
            await process_text(update, context, text)

        else:
            await update.message.reply_text("⚠️ Message type not supported.")

    except Exception as e:
        print(f"[Main Error] {e}")
        await update.message.reply_text("⚠️ A technical error occurred. Please try again later.")

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    if context.user_data.get("awaiting_name"):
        context.user_data["name"] = text.title()
        context.user_data["awaiting_name"] = False
        await update.message.reply_text(f"Nice to meet you, {context.user_data['name']} 😊")
        await start(update, context)
        return

    if text == "🌤 weather forecast":
        context.user_data["awaiting_city"] = True
        name = context.user_data.get("name", "friend")
        await update.message.reply_text("📍 Please specify the city to get the forecast:")

        return

    if text == "🗞 news":
        await update.message.reply_text("📡 Fetching the latest news...")
        news_list = fetch_news(language="en", limit=4)  # Changed to English
        for item in news_list:
            await update.message.reply_text(item)
        return

    if context.user_data.get("awaiting_city"):
        context.user_data["awaiting_city"] = False
        forecast = get_weather(text)
        if forecast:
            await update.message.reply_text(forecast)
        else:
            await update.message.reply_text("⚠️ Could not find the city or get the forecast. Please try again.")
        return

    trigger_words = ["show", "upload", "photo", "image", "download", "picture"]

    if text in ["/cinema", "movies", "watch", "cinema", "🎮 movies"]:
        await cinema_command(update, context)
        return

    if text == "🔍 search for a movie":
        context.user_data["awaiting_movie_title"] = True
        await update.message.reply_text("🎬 Please enter the movie title in English")
        return

    if context.user_data.get("awaiting_movie_title"):
        context.user_data["awaiting_movie_title"] = False
        movie = search_movie(text)
        if movie is None:
            await update.message.reply_text("⚠️ Movie not found.")
        elif "error" in movie:
            await update.message.reply_text(f"⚠️ Error: {movie['error']}")
        else:
            reply = (
                f"🎬 Title: {movie['title']} ({movie['year']})\n"
                f"⭐ IMDb: {movie['rating']}\n"
                f"📝 Plot: {movie['plot']}\n"
                f"🔗 Watch: {movie['imdb_link']}"
            )
            if movie['poster'] and movie['poster'] != "N/A":
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["🔍 Search for a movie", "🎮 Movies"], ["🔙 Main Menu"]]
        await update.message.reply_text("📽 Choose the next action:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "⭐ top rated movies":
        await update.message.reply_text("📊 Fetching top movies...")
        movies = get_top_movies()
        if not movies:
            await update.message.reply_text("⚠️ Could not retrieve the list of movies.")
            return

        for movie in movies:
            reply = (
                f"🎬 {movie['title']} ({movie['year']})\n"
                f"⭐ Rating: {movie['rating']}\n"
                f"📝 {movie['plot']}\n"
                f"🔗 {movie['link']}"
            )
            if movie['poster']:
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["⭐ Top Rated Movies", "🎮 Movies"], ["🔙 Main Menu"]]
        await update.message.reply_text("📽 Choose the next action:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text == "🎲 suggest a movie":
        keyboard = [
            ["Thriller", "Detective", "Sci-Fi"],
            ["Action", "Comedy", "Horror"],
            ["Fantasy", "Family", "Romance"],
            ["History", "Musical", "Disaster"],
            ["🔙 Main Menu"]
        ]
        await update.message.reply_text("🎬 Choose a genre:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text.lower() in GENRE_MAP:
        genre_id = GENRE_MAP[text.lower()]
        await update.message.reply_text(f"🎞 Searching for movies in the genre: {text.title()}...")
        movies = get_top_by_genre(genre_id)
        if not movies:
            await update.message.reply_text("⚠️ No movies found for this genre.")
            return

        for movie in movies:
            reply = (
                f"🎬 {movie['title']} ({movie['year']})\n"
                f"⭐ Rating: {movie['rating']}\n"
                f"📝 {movie['plot']}\n"
                f"🔗 {movie['link']}"
            )
            if movie['poster']:
                await update.message.reply_photo(photo=movie['poster'], caption=reply)
            else:
                await update.message.reply_text(reply)

        keyboard = [["🎲 Suggest a movie", "🎮 Movies"], ["🔙 Main Menu"]]
        await update.message.reply_text("🎯 Choose the next action:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    
    if text == "🧘 relax":
        keyboard = [["🌧 Rain", "🔥 Fireplace", "🎵 Relax"], ["🔙 Main Menu"]]
        await update.message.reply_text("🧘 Choose a relaxation mode:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if text in ["🌧 rain", "🔥 fireplace", "🎵 relax"]:
        sounds = {
            "🌧 rain": "https://www.youtube.com/watch?v=GxE6g1fLxoo",
            "🔥 fireplace": "https://www.youtube.com/watch?v=eyU3bRy2x44",
            "🎵 relaxmusic": "https://www.youtube.com/watch?v=2OEL4P1Rz04"
        }
        await update.message.reply_text(f"🎧 Enjoy relaxation: {sounds[text]}")
        return

    if text == "🔙 main menu":
        await start(update, context)
        return


    if text in ["ℹ️ help", "/help"]:
        await help_command(update, context)
        return
        
    if text in ["🗞 news", "/news"]:
        await news_command(update, context)
        return

    if text in ["queries", "dialogue", "/gpt", "💬 queries"]:
        await gpt_mode(update, context)
        return

    if text in ["tasks", "/plan", "design", "proposition","🗓 plan"]:
        context.user_data["awaiting_task"] = True
        await update.message.reply_text("📝 What exactly shall we plan? For example: 'Remind me in 10 minutes about the meeting'")
        return

    if context.user_data.get("awaiting_task"):
        context.user_data["awaiting_task"] = False
        parsed = parse_task_request(text)
        if parsed:
            task_text = parsed["task_text"].replace("remind", "", 1).strip()
            schedule_reminder(context, update.effective_chat.id, task_text, parsed["interval_sec"])
            await update.message.reply_text(f"✅ Reminder set\n⏳ I will remind you in {parsed['interval_sec'] // 60} minutes")
            return

        parsed_abs = parse_absolute_time_request(text)
        if parsed_abs:
            task_text = parsed_abs["task_text"].replace("remind", "", 1).strip()
            schedule_reminder(context, update.effective_chat.id, task_text, parsed_abs["interval_sec"])
            await update.message.reply_text(f"✅ Reminder set\n🕒 It will trigger at the specified time")
            return

        await update.message.reply_text("⚠️ Could not recognize the time. Please try again.")
        return

    if any(trigger in text for trigger in trigger_words):
        query = clean_query(text)
        await update.message.reply_text("🔍 Searching for an image...")
        result = get_image_url(query)
        if result.startswith("http"):
            await update.message.reply_photo(result)
        else:
            await update.message.reply_text(result)
        return

    await update.message.reply_text("🧠 Processing through GPT...")
    gpt_reply = ask_gpt(text)
    try:
        await update.message.reply_text(gpt_reply)
    except:
        await update.message.reply_text("⚠️ Could not display GPT's response.")

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

    # 🧠 Mood request async wrapper function
    async def run_send_mood():
        await send_mood_request(app)

    # ⏰ Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_send_mood, CronTrigger(hour=8, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=12, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=16, minute=0))
    scheduler.add_job(run_send_mood, CronTrigger(hour=19, minute=0))  # test
    scheduler.start()

    print("🟢 Bot is running. Open Telegram and type /start")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

