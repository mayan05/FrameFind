import requests 
import pandas as pd
import sqlalchemy as sa
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("TMDB_API_KEY")
base_url =  "https://api.themoviedb.org/3"
movies = []

if not api_key: # Couldnt find the api key
    raise ValueError("TMDB_API_KEY environment variable not set.")

# Fetch genres
genre_url = f"{base_url}/genre/movie/list?api_key={api_key}"
genre_response = requests.get(genre_url).json()
genres_map = {genre["id"]: genre["name"] for genre in genre_response["genres"]}
print(f"Genres fetched: {len(genres_map)} genres")

print("Collecting data from TMDB...")

for page in range(1,51): # Collecting 1000 popular movies
    url = f"{base_url}/movie/popular?api_key={api_key}&page={page}"
    response = requests.get(url).json()
    for movie in response["results"]:
           movies.append({
               "movie_id": movie["id"],
               "title": movie["title"],
               "genres": ",".join([genres_map.get(g_id, "Unknown") for g_id in movie.get("genre_ids", [])] or ["Unknown"]),
               "release_year": int(movie["release_date"][:4]) if movie["release_date"] else 0,
               "overview": movie["overview"] or "No description"
           }) 

df = pd.DataFrame(movies)

engine = sa.create_engine("mysql+mysqlconnector://root:12345678@localhost/movies_db")  # Replace with your credentials
df.to_sql("movies", engine, if_exists="replace", index=False)

def get_genre(movie_id: int):
    pass

print(f"Length of the Movies dataframe: {len(df)}")