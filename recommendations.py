import pandas as pd
import sqlalchemy as sa
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
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

# Collaborative filtering setup
ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", engine)
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings[['user_id', 'movie_id', 'rating']], reader)
trainset = data.build_full_trainset()
svd = SVD()
svd.fit(trainset)

def get_content_recommendations(title, n=5):
    try:
        matches = movies[movies["title"].str.contains(title, case=False, na=False)]
        if matches.empty:
            return ["Movie not found"]
        idx = matches.index[0]
        sim_scores = sorted(list(enumerate(similarity_matrix[idx])), key=lambda x: x[1], reverse=True)
        return movies["title"].iloc[[i[0] for i in sim_scores[1:n+1]]].tolist()
    except IndexError:
        return ["Movie not found"]

def get_collaborative_recommendations(user_id, n=5):
    try:
        # Get movies the user has rated
        rated_movies = ratings[ratings["user_id"] == user_id]["movie_id"].tolist()
        all_movie_ids = movies["movie_id"].tolist()
        unrated_movie_ids = [mid for mid in all_movie_ids if mid not in rated_movies]
        
        # Predict ratings for unrated movies
        predictions = [(mid, svd.predict(user_id, mid).est) for mid in unrated_movie_ids]
        predictions.sort(key=lambda x: x[1], reverse=True)
        top_movie_ids = [mid for mid, _ in predictions[:n]]
        return movies[movies["movie_id"].isin(top_movie_ids)]["title"].tolist()
    except Exception:
        return ["No collaborative recommendations available"]