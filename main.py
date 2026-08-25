import os
import sqlite3
from importlib import import_module

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Cloudinary configuration
cloudinary = None
cloudinary_uploader = None
if os.environ.get("CLOUDINARY_CLOUD_NAME"):
    cloudinary = import_module("cloudinary")
    cloudinary_uploader = import_module("cloudinary.uploader")

if cloudinary:
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    )

psycopg2 = None
psycopg2_extras = None
if os.environ.get("DATABASE_URL"):
    psycopg2 = import_module("psycopg2")
    psycopg2_extras = import_module("psycopg2.extras")

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    if DATABASE_URL:
        connection = psycopg2.connect(DATABASE_URL)
        connection.cursor_factory = psycopg2_extras.RealDictCursor
        return connection

    os.makedirs(app.instance_path, exist_ok=True)
    connection = sqlite3.connect(os.path.join(app.instance_path, "heritage.db"))
    connection.row_factory = sqlite3.Row
    return connection


def get_insert_placeholder():
    return "%s" if DATABASE_URL else "?"


with app.app_context():
    connection = get_db()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS place (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                location VARCHAR(255),
                image TEXT,
                description TEXT
            )
            """
        )
    else:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS place (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                location TEXT,
                image TEXT,
                description TEXT
            )
            """
        )

    connection.commit()
    cursor.close()
    connection.close()


@app.route("/")
def index():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM place")
    places = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("index.html", places=places)


@app.route("/add", methods=("GET", "POST"))
def add_place():
    connection = get_db()
    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        description = request.form["description"]
        image_file = request.files.get("image")

        image_url = None
        if image_file and cloudinary:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get("secure_url")

        placeholder = get_insert_placeholder()
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO place (title, location, image, description) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
            (title, location, image_url, description),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("index"))

    return render_template("add.html")


if __name__ == "__main__":
    app.run(debug=True)