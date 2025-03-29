from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from routes.upload import upload_bp
from routes.notes import notes_bp
from routes.api import api_bp
import os

# Load .env vars
load_dotenv()

# Set up Flask and manually define template + static folders
app = Flask(
    __name__,
    template_folder="../frontend/templates",  # <-- updated path
    static_folder="static"                   # where CSS/JS go (unchanged)
)
app.config["UPLOAD_FOLDER"] = "uploads"
app.register_blueprint(upload_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(api_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    # You’ll handle file saving and processing later
    return redirect(url_for("processing"))

@app.route("/processing")
def processing():
    return render_template("processing.html")

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)
