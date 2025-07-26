from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlalchemy as sa
from recommendations import get_content_recommendations, get_collaborative_recommendations
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
engine = sa.create_engine(os.getenv("DB_URL"))

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        movies = pd.read_sql("SELECT movie_id, title, genres, release_year FROM movies ORDER BY title", engine)
        if movies.empty:
            return render_template("index.html", error="No movies found in database.", movies=[], recommendations=[], selected_movie=None, no_match=True, collab_recommendations=[])
    except Exception as e:
        return render_template("index.html", error=f"Database error: {str(e)}", movies=[], recommendations=[], selected_movie=None, no_match=True, collab_recommendations=[])

    recommendations = []
    selected_movie = None
    no_match = False
    collab_recommendations = []
    
    if request.method == "POST":
        try:
            movie_title = request.form["movie_title"].strip()
            print(f"Searching for: {movie_title}")
            recommendations = get_content_recommendations(movie_title)
            print(f"Content Recommendations: {recommendations}")
            if recommendations == ["Movie not found"]:
                no_match = True
                selected_movie = "Not found"
            else:
                selected_movie_df = movies[movies["title"].str.contains(movie_title, case=False, na=False)]
                if not selected_movie_df.empty:
                    selected_movie = selected_movie_df["title"].iloc[0]
                else:
                    no_match = True
                    selected_movie = "Not found"
            # Collaborative recommendations for user_id 1 (example)
            collab_recommendations = get_collaborative_recommendations(1)
            print(f"Collaborative Recommendations: {collab_recommendations}")
        except (ValueError, IndexError) as e:
            recommendations = ["Invalid input"]
            no_match = True
            selected_movie = "Not found"
            print(f"Error in recommendations: {str(e)}")

    return render_template("index.html", movies=movies.to_dict("records"), 
                         recommendations=recommendations, selected_movie=selected_movie, 
                         no_match=no_match, collab_recommendations=collab_recommendations)

@app.route("/rate", methods=["POST"])
def rate():
    try:
        user_id = int(request.form["user_id"])
        movie_id = int(request.form["movie_id"])
        rating = float(request.form["rating"])
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        if not (1 <= user_id <= 100):
            return jsonify({"error": "User ID must be between 1 and 100"}), 400
        with engine.connect() as conn:
            user_exists = conn.execute(
                sa.text("SELECT 1 FROM users WHERE user_id = :user_id"), 
                {"user_id": user_id}
            ).fetchone()
            movie_exists = conn.execute(
                sa.text("SELECT 1 FROM movies WHERE movie_id = :movie_id"), 
                {"movie_id": movie_id}
            ).fetchone()
            if not user_exists:
                return jsonify({"error": "User ID does not exist"}), 400
            if not movie_exists:
                return jsonify({"error": "Movie ID does not exist"}), 400
        pd.DataFrame([{
            "user_id": user_id,
            "movie_id": movie_id,
            "rating": rating,
            "timestamp": pd.Timestamp.now()
        }]).to_sql("ratings", engine, if_exists="append", index=False)
        return jsonify({"message": "Rating submitted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)