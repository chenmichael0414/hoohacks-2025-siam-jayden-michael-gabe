from flask import Blueprint, request, redirect, url_for, current_app
import os
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return "No video file part", 400

    file = request.files["video"]

    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    # You can store the filename in session, DB, etc. if needed
    return redirect(url_for("processing"))