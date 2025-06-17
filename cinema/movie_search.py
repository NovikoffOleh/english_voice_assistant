import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def search_movie(query: str) -> dict | None:
    if not OMDB_API_KEY:
        return {"error": "OMDB API key is missing"}

    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "OMDb API error"}

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

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    movies = []
    for movie in data.get("results", [])[:10]:
        movies.append({
            "title": movie.get("title"),
            "year": movie.get("release_date", "")[:4],
            "rating": movie.get("vote_average"),
            "plot": movie.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
            "link": f"https://www.themoviedb.org/movie/{movie.get('id')}"
        })

    return movies


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

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    movies = []
    for movie in data.get("results", [])[:5]:
        movies.append({
            "title": movie.get("title"),
            "year": movie.get("release_date", "")[:4],
            "rating": movie.get("vote_average"),
            "plot": movie.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
            "link": f"https://www.themoviedb.org/movie/{movie.get('id')}"
        })

    return movies
