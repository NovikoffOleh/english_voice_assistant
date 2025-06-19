import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def search_movie(query: str) -> dict | None:
    if not OMDB_API_KEY:
        return {"error": "OMDb API key is missing."}

    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={query}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            return None

        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "rating": data.get("imdbRating"),
            "plot": data.get("Plot"),
            "poster": data.get("Poster"),
            "imdb_link": f"https://www.imdb.com/title/{data.get('imdbID')}"
        }
    except Exception as e:
        return {"error": f"OMDb API request failed: {e}"}


def get_top_movies() -> list:
    if not TMDB_API_KEY:
        return []

    today = datetime.today()
    year = today.year

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "vote_average.desc",
        "primary_release_year": year,
        "vote_count.gte": 100,
        "page": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[TMDb Top Movies] ❌ {e}")
        return []

    return [
        {
            "title": m.get("title"),
            "year": m.get("release_date", "")[:4],
            "rating": m.get("vote_average"),
            "plot": m.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
            "link": f"https://www.themoviedb.org/movie/{m.get('id')}"
        }
        for m in data.get("results", [])[:10]
    ]


def get_top_by_genre(genre_id: int) -> list:
    if not TMDB_API_KEY:
        return []

    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "vote_average.desc",
        "with_genres": genre_id,
        "vote_count.gte": 100,
        "page": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[TMDb Genre Search] ❌ {e}")
        return []

    return [
        {
            "title": m.get("title"),
            "year": m.get("release_date", "")[:4],
            "rating": m.get("vote_average"),
            "plot": m.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get("poster_path") else None,
            "link": f"https://www.themoviedb.org/movie/{m.get('id')}"
        }
        for m in data.get("results", [])[:5]
    ]
