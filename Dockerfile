 FROM python:3.10-slim
 
 WORKDIR /app

 # Install system dependencies for Cython compilation
 RUN apt-get update && apt-get install -y \
     build-essential \
     gcc \
     && rm -rf /var/lib/apt/lists/*

 # Copy and install Python dependencies
 COPY requirements.txt .
 RUN pip install --no-cache-dir -r requirements.txt

 # Copy only necessary application files
 COPY app.py recommendations.py templates/ static/ ./

 # Run the app with gunicorn
 CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2", "app:app"]