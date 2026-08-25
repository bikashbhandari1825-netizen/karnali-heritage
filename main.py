import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# Cloudinary Configuration (Free Cloud Storage for Photos)
# These are standard test/development keys or your cloud settings
import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key = os.environ.get("CLOUDINARY_API_KEY"),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
)

import os
import psycopg2
import psycopg2.extras

# Get the cloud database URL from Render's environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    if DATABASE_URL:
        # If running on Render, connect to the Neon Cloud PostgreSQL database
        connection = psycopg2.connect(DATABASE_URL)
        connection.cursor_factory = psycopg2.extras.RealDictCursor
        return connection
    else:
        # If running locally on your laptop, use SQLite as a fallback
        os.makedirs(app.instance_path, exist_ok=True)
        connection = sqlite3.connect(os.path.join(app.instance_path, "heritage.db"))
        connection.row_factory = sqlite3.Row
        return connection

# Create database table automatically if not exists
with app.app_context():
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS place (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            image TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

# Home Route: Displays all uploaded places with permanent cloud images
@app.route("/")
def index():
    connection = get_db()
    places = connection.execute("SELECT * FROM place").fetchall()
    connection.close()
    return render_template("index.html", places=places)

# Add Place Route: Uploads image directly to Cloudinary
@app.route("/add", methods=("GET", "POST"))
def add_place():
    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        description = request.form["description"]
        image_file = request.files["image"]

        if image_file:
            # Upload image to Cloudinary cloud storage
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get("secure_url")

            connection = get_db()
            connection.execute(
                "INSERT INTO place (title, location, image, description) VALUES (?, ?, ?, ?)",
                (title, location, image_url, description)
            )
            connection.commit()
            connection.close()
            return redirect(url_for("index"))

    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)