# translator.py
from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"[Translator] Error: {str(e)}")
        return text  # Повертаємо оригінал у разі помилки
