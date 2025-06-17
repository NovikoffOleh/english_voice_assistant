import os
import requests
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

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

def search_top_by_genre(genre_key: str) -> list:
    genre_samples = {
        "thriller": ["Prisoners", "Gone Girl", "Se7en", "The Girl with the Dragon Tattoo", "Zodiac"],
        "detective": ["Sherlock Holmes", "Knives Out", "Murder on the Orient Express", "The Nice Guys", "The Hound of the Baskervilles"],
        "sci-fi": ["Interstellar", "Arrival", "Blade Runner 2049", "The Matrix", "Inception"],
        "action": ["John Wick", "Mad Max: Fury Road", "Extraction", "Gladiator", "Skyfall"],
        "comedy": ["The Hangover", "Superbad", "Step Brothers", "The Grand Budapest Hotel", "Free Guy"],
        "horror": ["The Conjuring", "Get Out", "Hereditary", "The Babadook", "A Quiet Place"],
        "fantasy": ["The Lord of the Rings", "Harry Potter and the Sorcerer's Stone", "The Witcher", "Pan's Labyrinth", "Stardust"],
        "kids": ["Inside Out", "Finding Nemo", "Toy Story", "Zootopia", "Frozen"],
        "romance": ["Pride and Prejudice", "La La Land", "The Notebook", "Titanic", "Before Sunrise"],
        "historical": ["Braveheart", "Schindler's List", "The King's Speech", "12 Years a Slave", "The Imitation Game"],
        "musical": ["The Greatest Showman", "Les Misérables", "West Side Story", "Chicago", "La La Land"],
        "disaster": ["The Day After Tomorrow", "2012", "San Andreas", "Greenland", "Twister"]
    }

    titles = genre_samples.get(genre_key.lower(), [])
    results = []

    for title in titles:
        movie = search_movie(title)
        if movie:
            results.append(movie)

    return results
