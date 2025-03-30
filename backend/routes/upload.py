from flask import Blueprint, request, redirect, url_for, current_app, session
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"mp4", "mov", "mp3", "pptx", "pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return "No file part", 400

    file = request.files["video"]

    if file.filename == "":
        return "No selected file", 400

    if not allowed_file(file.filename):
        return "File type not allowed", 400

    filename = secure_filename(file.filename)
    session["filename"] = filename
    session["file_type"] = filename.rsplit(".", 1)[1].lower()
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    print(session.get("filename"))
    file.save(save_path)
    print(session.get("filename"))

    # Optional: store file type or extension if you want to branch processing logic later
    return redirect(url_for("processing"))