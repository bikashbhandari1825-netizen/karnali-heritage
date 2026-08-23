import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Photo saving folder and database settings.
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
DATABASE = os.path.join(app.instance_path, "heritage.db")


def get_db():
    os.makedirs(app.instance_path, exist_ok=True)
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


with app.app_context():
    connection = get_db()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS place (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            image TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db()
    places = connection.execute("SELECT * FROM place ORDER BY id").fetchall()
    connection.close()
    return render_template("index.html", places=places)


@app.route("/add", methods=["GET", "POST"])
def add_place():
    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        description = request.form["description"]

        file = request.files.get("image")

        if file and file.filename:
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_url = f"uploads/{filename}"
        else:
            return render_template("add.html", error="Please upload an image.")

        connection = get_db()
        connection.execute(
            "INSERT INTO place (title, location, image, description) VALUES (?, ?, ?, ?)",
            (title, location, image_url, description),
        )
        connection.commit()
        connection.close()
        return redirect(url_for("home"))

    return render_template("add.html")


if __name__ == "__main__":
    app.run(debug=True)  