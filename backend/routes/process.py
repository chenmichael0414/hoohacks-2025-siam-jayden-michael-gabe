import os
import ffmpeg
from flask import session, Blueprint, render_template
from services import transcription, slides

process_bp = Blueprint("process", __name__)

@process_bp.route("/processing")
def processing_page():
    filename = session.get("filename")
    print(session)
    print(filename)
    print("got here 2")
    if not filename:
        return "No file uploaded", 400
    file_type = session.get("file_type")
    output_file = "lecture_to_audio.mp3"

    # Emit progress: Audio extraction starts
    
    match file_type:
        case "mp4" | "mov":
            ffmpeg.input(filename).output(output_file, format="mp3", audio_bitrate="128k").run()
        case "mp3":
            os.rename(filename, output_file)  
    print(transcription.transcribe_audio(filename))
    

    return render_template("processing.html")

    

    # case "pdf":
