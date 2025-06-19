# modules/mood_checker.py

from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from modules.gpt_handler import ask_gpt

MOOD_EMOJIS = [
    ("😡", "angry"),
    ("😒", "sad"),
    ("😃", "happy"),
    ("🤒", "sick"),
    ("🥰", "in love"),
    ("🥱", "tired")
]

MOOD_CALLBACKS = {
    "angry": "😡",
    "sad": "😒",
    "happy": "😃",
    "sick": "🤒",
    "love": "🥰",
    "tired": "🥱"
}

def get_mood_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="😡", callback_data="mood_angry"),
            InlineKeyboardButton(text="😒", callback_data="mood_sad"),
            InlineKeyboardButton(text="😃", callback_data="mood_happy")
        ],
        [
            InlineKeyboardButton(text="🤒", callback_data="mood_sick"),
            InlineKeyboardButton(text="🥰", callback_data="mood_love"),
            InlineKeyboardButton(text="🥱", callback_data="mood_tired")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def send_mood_request(app):
    for user_id, data in app.user_data.items():
        name = data.get("name", "friend")
        try:
            await app.bot.send_message(
                chat_id=user_id,
                text=f"👀 Hey {name}, how are you feeling? Choose an emoji:",
                reply_markup=get_mood_keyboard()
            )
        except Exception as e:
            print(f"[Mood Scheduler Error] User {user_id}: {e}")

async def handle_mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mood_key = query.data.replace("mood_", "")
    emoji = MOOD_CALLBACKS.get(mood_key, "😐")
    name = context.user_data.get("name", "friend")

    hour = datetime.now().hour
    part_of_day = (
        "this morning" if 5 <= hour < 12 else
        "this afternoon" if 12 <= hour < 17 else
        "this evening"
    )

    mood_prompt = (
        f"{emoji} {name} feels '{mood_key}' {part_of_day}. "
        f"Give a short and friendly 1–2 sentence reply, using 'you' casually. "
        f"Add a quick daily forecast like a modern astrologer or lifestyle coach — "
        f"emotional, casual, positive, no mysticism. "
        f"No formal tone or phrases like 'dear user'. "
        f"Keep it fresh, English, and concise."
    )

    try:
        response = ask_gpt(mood_prompt)
        await query.edit_message_text(f"{emoji} {name}, {response}")
    except Exception as e:
        await query.edit_message_text(f"⚠️ Something went wrong. Try again. ({e})")
