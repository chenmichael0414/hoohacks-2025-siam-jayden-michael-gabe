import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app
from services import transcription, slides

process_bp = Blueprint("process", __name__)

@process_bp.route("/processing")
def processing_page():
    filename = session.get("filename")
    if not filename:
        return "No file uploaded", 400
    file_type = session.get("file_type")
    file_path = session.get("file_path")
    output_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_to_audio.mp3")
    # Emit progress: Audio extraction starts
    
    match file_type:
        case "mp4" | "mov":
            ffmpeg.input(filename).output(output_file_path, format="mp3", audio_bitrate="128k").run()
        case "mp3":
            os.rename(file_path, output_file_path)  
    print(file_path)
    print(transcription.transcribe_audio(output_file_path))
    

    return render_template("processing.html")

    

    # case "pdf":
