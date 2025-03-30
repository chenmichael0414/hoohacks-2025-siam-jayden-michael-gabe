from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from routes.upload import upload_bp
from routes.notes import notes_bp
from routes.auth import auth_bp
from services.auth_config import oauth  # Auth0 setup is imported from here
import os

# Load environment variables from .env
load_dotenv()

# Set up Flask app with frontend paths
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
app.config["UPLOAD_FOLDER"] = "uploads"

# Initialize OAuth (for Auth0)
oauth.init_app(app)

# Register blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(auth_bp)


# Main routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    return redirect(url_for("processing"))


@app.route("/processing")
def processing():
    return render_template("processing.html")


@app.route("/results")
def results():
    return render_template("results.html")


if __name__ == "__main__":
    app.run(debug=True)
