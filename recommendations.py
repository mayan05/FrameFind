import pandas as pd
import sqlalchemy as sa
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()
engine = sa.create_engine(os.getenv("DB_URL"))

# Fetch movies
movies = pd.read_sql("SELECT movie_id, title, overview, genres FROM movies", engine)

# Combine overview and genres for TF-IDF
movies["combined"] = movies["overview"].fillna("") + " " + movies["genres"].fillna("")

# TF-IDF vectorization
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(movies["combined"])
similarity_matrix = cosine_similarity(tfidf_matrix)

def get_recommendations(title, n=5):
    try:
        idx = movies[movies["title"].str.contains(title, case=False, na=False)].index[0]
        sim_scores = sorted(list(enumerate(similarity_matrix[idx])), key=lambda x: x[1], reverse=True)
        return movies["title"].iloc[[i[0] for i in sim_scores[1:n+1]]].tolist()
    except IndexError:
        return ["Movie not found"]