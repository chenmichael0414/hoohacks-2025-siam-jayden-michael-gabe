import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app
from services import transcription, slides
from services.video import detect_and_write_slides_from_video

process_bp = Blueprint("process", __name__)


@process_bp.route("/processing")
def processing_page():
    filename = session.get("filename")
    if not filename:
        return "No file uploaded", 400
    file_type = session.get("file_type")
    input_file_path = session.get("file_path")
    output_file_path = None
    video_output_file_path = None
    print(input_file_path)
    match file_type:
        case "mp4" | "mov":
            output_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_to_audio.mp3")
            video_output_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_video.mp4")
        case "mp3":
            output_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_to_audio.mp3")
        case _:
            raise TypeError("Invalid file type! Your choices are: mp4, mov, mp3, pdf, and pptx.")

    if os.path.exists(output_file_path):
        match file_type:
            case "mp4" | "mov":
                ffmpeg.input(filename).output(input_file_path, format="mp3", audio_bitrate="128k").run()
            case "mp3":
                print(output_file_path)
                os.replace(input_file_path, output_file_path)
            case "pdf":
                pass

    else:
        match file_type:
            case "mp4" | "mov":
                ffmpeg.input(filename).output(output_file_path, format="mp3", audio_bitrate="128k").run()
            case "mp3":
                os.rename(input_file_path, output_file_path)
    match file_type:
        case "mp4" | "mov":
            print(transcription.transcribe_audio(output_file_path))
            print(detect_and_write_slides_from_video(video_output_file_path))
        case "mp3":
            print(transcription.transcribe_audio(output_file_path))
        case "pdf":
            print(slides.parse_generate_pdf(input_file_path))

    return render_template("processing.html")
