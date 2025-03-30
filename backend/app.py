from flask import Flask, render_template, request, redirect, url_for, session, send_file
from dotenv import load_dotenv
from routes.upload import upload_bp
from routes.notes import notes_bp
from routes.auth import auth_bp
from routes.process import process_bp
from routes.check_pdf import check_pdf_bp
from flask import send_file
from datetime import datetime
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
app.register_blueprint(process_bp)
app.register_blueprint(check_pdf_bp)


# Main routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lecture_notes.pdf")
def serve_lecture_notes():
    # Get absolute path to lecture_notes.pdf in the base repo
    base_dir = os.path.abspath(os.path.dirname(__file__))  # This is /backend
    pdf_path = os.path.join(base_dir, "..", "lecture_notes.pdf")  # Go up one level
    pdf_path = os.path.abspath(pdf_path)  # Clean it up

    if not os.path.exists(pdf_path):
        return "PDF not found", 404

    return send_file(pdf_path, mimetype='application/pdf')

# About page
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/upload", methods=["POST"])
def upload():
    return redirect(url_for("processing"))


@app.route("/processing")
def processing():
    return render_template("processing.html")


@app.route("/results")
def results():
    return render_template("results.html", timestamp=datetime.utcnow().timestamp())


@app.route("/download")
def download():
    root_path = os.getcwd()
    file_path = os.path.join(root_path, 'lecture_notes.pdf')  # Build the path to the file

    if os.path.exists(file_path):  # Check if the file exists
        return send_file(file_path, as_attachment=True)  # Send the file as an attachment
    else:
        return "File not found", 404  # Return a 404 error if the file is not found



if __name__ == "__main__":
    app.run(host="localhost", port=0000, debug=True)