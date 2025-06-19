import os
import requests
import string
from dotenv import load_dotenv
from modules.translator import translate_to_english

# Load API keys
load_dotenv()
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# 🧼 Clean input query from extra words and punctuation
def clean_query(text):
    stopwords = ["show", "download", "photo", "image", "picture"]
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    filtered = [word for word in words if word not in stopwords]
    return " ".join(filtered)

# 🔍 Search Unsplash
def search_unsplash(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["urls"]["regular"]
    except Exception as e:
        print(f"[Unsplash] ❌ {e}")
        return None

# 🔍 Search Pixabay
def search_pixabay(query):
    try:
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page=1&safesearch=true"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["hits"]:
            return data["hits"][0]["largeImageURL"]
        return None
    except Exception as e:
        print(f"[Pixabay] ❌ {e}")
        return None

# 🔄 Main function for getting image URL
def get_image_url(raw_query):
    try:
        cleaned_query = clean_query(raw_query)
        translated_query = translate_to_english(cleaned_query)

        image_url = search_unsplash(translated_query)
        if image_url:
            return image_url

        image_url = search_pixabay(translated_query)
        if image_url:
            return image_url

        return "❌ No image found on Unsplash or Pixabay."
    except Exception as e:
        return f"❌ Image search error: {str(e)}"
