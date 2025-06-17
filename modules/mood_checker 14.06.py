from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from modules.gpt_handler import ask_gpt

MOOD_EMOJIS = [
    ("😡", "не в гуморі"),
    ("😒", "сумно"),
    ("😃", "гарний настрій"),
    ("🤒", "хворію"),
    ("🥰", "кохання"),
    ("🥱", "стомився")
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
        name = data.get("name", "друже")
        try:
            await app.bot.send_message(
                chat_id=user_id,
                text=f"👀 {name}, як твій настрій? Обери емодзі:",
                reply_markup=get_mood_keyboard()
            )
        except Exception as e:
            print(f"[Mood Scheduler Error] User {user_id}: {e}")

async def handle_mood_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mood_key = query.data.replace("mood_", "")
    emoji = MOOD_CALLBACKS.get(mood_key, "😐")
    name = context.user_data.get("name", "друже")

    # Визначаємо частину доби
    hour = datetime.now().hour
    part_of_day = (
        "вранці" if 5 <= hour < 12 else
        "вдень" if 12 <= hour < 17 else
        "увечері"
    )

    # Оновлений prompt для GPT
    mood_prompt = (
        f"{emoji} {name} почувається '{mood_key}' {part_of_day}. "
        f"Дай коротку відповідь (1–2 речення), звертаючись на 'ти'. "
        f"Не використовуй слова 'ви', 'вас', або шаблонні фрази. "
        f"Відповідь має бути сучасна, проста, дружня. "
        f"Враховуй частину доби: поради мають бути доречними саме зараз (наприклад: ввечері — відпочинок, вдень — активність)."
        f"Не вигадуй слова. Роби формулювання короткими і змістовними"
        f"Будь як таролог. Давай можливий прогноз подій на 4 години в гумористичній формі"
    )

    try:
        response = ask_gpt(mood_prompt)
        await query.edit_message_text(f"{emoji} {name}, {response}")
    except Exception as e:
        await query.edit_message_text(f"⚠️ Сталася помилка. Спробуй ще раз. ({e})")
