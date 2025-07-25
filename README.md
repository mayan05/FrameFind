# FRAME FIND

This project implements a movie recommendation system using Flask for the web application, pandas for data manipulation, sqlalchemy for database interaction, and scikit-learn for content-based recommendations.

## Setup Instructions

Follow these steps to set up and run the application locally:

### 1. Prerequisites

*   **Python 3.10+**: Ensure you have Python installed.
*   **MySQL Server**: A running MySQL server is required.

### 2. Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```
DB_URL="mysql+mysqlconnector://user:password@host:port/movies_db"
TMDB_API_KEY="your_tmdb_api_key"
```

*   Replace `user`, `password`, `host`, and `port` with your MySQL database credentials.
*   Get your `TMDB_API_KEY` from [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api).

### 3. Install Dependencies

It is recommended to create a virtual environment:

```bash
python -m venv venv
./venv/Scripts/activate  # On Windows
source venv/bin/activate # On macOS/Linux
```

Then install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Database Initialization and Population

First, ensure your MySQL server is running. Then, connect to your MySQL server and run the `db/schema.sql` file to create the database:

```bash
mysql -u your_username -p movies_db < db/schema.sql
```

Now, run the `populate.py` script to create the tables and populate them with movie data:

```bash
python db/populate.py
```

This script will fetch movie data from TMDB and populate your database.

### 5. Run the Application

```bash
python app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Project Structure

*   `app.py`: The main Flask application.
*   `recommendations.py`: Contains the recommendation logic.
*   `db/`: Database related files.
*   `templates/`: HTML templates for the web interface.
*   `requirements.txt`: Python dependencies.
*   `.env`: Environment variables (not committed to Git). 