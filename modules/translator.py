from deep_translator import GoogleTranslator
import langdetect

def is_english(text: str) -> bool:
    try:
        return langdetect.detect(text) == "en"
    except:
        return False

def safe_translate(text: str, target_lang: str = "en") -> str:
    if not text or len(text.strip()) < 3:
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        print(f"[Translator] Error: {str(e)}")
        return text

def translate_to_english(text: str) -> str:
    if is_english(text):
        return text
    return safe_translate(text, target_lang="en")

def translate(text: str, target_lang: str = "en") -> str:
    if target_lang == "en" and is_english(text):
        return text
    return safe_translate(text, target_lang)
