# translator.py
from deep_translator import GoogleTranslator

def translate_to_english(text: str) -> str:
    """
    Optional function — used only if the input is in another language.
    In this EN-only version, it may be disabled or omitted.
    """
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"[Translator] Error: {str(e)}")
        return text  # Return original if translation fails

def translate(text: str, target_lang: str = "en") -> str:
    """
    Translates text into target language (e.g. en, uk, fr, de).
    In EN-only version, this function can be used to translate to other languages if needed.
    """
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"[Translator] Error: {str(e)}")
        return text
