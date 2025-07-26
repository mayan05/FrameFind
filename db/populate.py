import requests 
import pandas as pd
import sqlalchemy as sa
import os
from dotenv import load_dotenv

load_dotenv()

ratings = pd.read_csv("./u.data", sep="\t", names=["user_id", "movie_id", "rating", "timestamp"])
links = pd.read_csv("./links.csv")

api_key = os.environ.get("TMDB_API_KEY")
base_url =  "https://api.themoviedb.org/3"
movies = []

if not api_key: # Couldnt find the api key
    raise ValueError("TMDB_API_KEY environment variable not set.")

print("\nCollecting the Genres and their ids...")

# Fetching genres
genre_url = f"{base_url}/genre/movie/list?api_key={api_key}"
genre_response_obj = requests.get(genre_url)

if genre_response_obj.status_code != 200:
    print(f"Error fetching genres. Status Code: {genre_response_obj.status_code}")
    print(f"Response text: {genre_response_obj.text}")
    raise ConnectionError("Failed to fetch genres from TMDB API. Check API key and network connectivity.")

genre_response = genre_response_obj.json()

if "genres" not in genre_response:
    print("Error: 'genres' key not found in TMDB genre response.")
    print(f"Full genre response: {genre_response}")
    raise KeyError("'genres' key missing from TMDB genre response. Check API key and network connectivity.")

genres_map = {genre["id"]: genre["name"] for genre in genre_response["genres"]}
print(f"Genres fetched: {len(genres_map)} genres")

print("\nCollecting data from TMDB...")

for page in range(1,501): # Collecting 10000 popular movies
    url = f"{base_url}/movie/popular?api_key={api_key}&page={page}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching popular movies page {page}. Status Code: {response.status_code}")
        print(f"Response text: {response.text}")
        raise ConnectionError(f"Failed to fetch popular movies from TMDB API for page {page}. Check API key and network connectivity.")

    response_json = response.json()
    if "results" not in response_json:
        print(f"Error: 'results' key not found in TMDB popular movies response for page {page}.")
        print(f"Full response: {response_json}")
        raise KeyError(f"'results' key missing from TMDB popular movies response for page {page}. Check API key and network connectivity.")

    for movie in response_json["results"]:
           movies.append({
               "movie_id": movie["id"],
               "title": movie["title"],
               "genres": ",".join([genres_map.get(g_id, "Unknown") for g_id in movie.get("genre_ids", [])] or ["Unknown"]),
               "release_year": int(movie["release_date"][:4]) if movie["release_date"] else 0,
               "overview": movie["overview"] or "No description"
           })
df = pd.DataFrame(movies)
print(f"\nSuccessfully collected {len(df)} movies")

engine = sa.create_engine(os.environ.get("DB_URL")) 
df.to_sql("movies", engine, if_exists="replace", index=False)

users = pd.DataFrame({
    "user_id": range(1, 101),
    "username": [f"user_{i}" for i in range(1, 101)]
})

users.to_sql("users", engine, if_exists="replace", index=False)
print("Users populated successfully!")


ratings = ratings.merge(links[["movieId", "tmdbId"]], left_on="movie_id", right_on="movieId", how="left")
ratings = ratings[["user_id", "tmdbId", "rating", "timestamp"]]
ratings.columns = ["user_id", "movie_id", "rating", "timestamp"]

movies = pd.read_sql("SELECT movie_id FROM movies", engine)
ratings = ratings[ratings["movie_id"].isin(movies["movie_id"])]

ratings = ratings[ratings["user_id"].isin(range(1, 101))]

ratings["timestamp"] = pd.to_datetime(ratings["timestamp"], unit="s")

ratings[["user_id", "movie_id", "rating", "timestamp"]].to_sql("ratings", engine, if_exists="replace", index=False)

print(f"Ratings populated successfully! {len(ratings)} ratings added.")