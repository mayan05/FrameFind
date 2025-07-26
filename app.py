from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlalchemy as sa
from recommendations import get_recommendations
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
engine = sa.create_engine(os.getenv("DB_URL"))

@app.route("/", methods=["GET", "POST"])
def home():
    # Fetch movies for dropdown and potential matching
    movies = pd.read_sql("SELECT movie_id, title FROM movies ORDER BY title", engine)
    recommendations = []
    selected_movie = None
    no_match = False
    
    if request.method == "POST":
        try:
            movie_title = request.form["movie_title"].strip()
            recommendations = get_recommendations(movie_title)
            if recommendations == ["Movie not found"]:
                no_match = True
                selected_movie = "Not found"
            else:
                selected_movie = movies[movies["title"].str.contains(movie_title, case=False, na=False)]["title"].iloc[0]
        except (ValueError, IndexError):
            recommendations = ["Invalid input"]
            no_match = True
            selected_movie = "Not found"
    
    return render_template("index.html", movies=movies.to_dict("records"), 
                         recommendations=recommendations, selected_movie=selected_movie, no_match=no_match)

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
        
        # Verify user_id and movie_id exist
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
        # Insert rating
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