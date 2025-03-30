import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app
from services import transcription, slides, video  # 🧠 include video.py from services

process_bp = Blueprint("process", __name__)


@process_bp.route("/processing")
def processing_page():
    filename = session.get("filename")
    if not filename:
        return "No file uploaded", 400

    file_type = session.get("file_type")
    input_file_path = session.get("file_path")
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    output_file_path = os.path.join(upload_folder, "lecture_to_audio.mp3")

    if not input_file_path or not os.path.exists(input_file_path):
        return "Invalid file path", 400

    try:
        transcript = ""
        slide_notes = ""

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        if file_type in ["mp4", "mov"]:
            print("🖼️ Detecting slide notes...")
            notes = video.process_video(input_file_path)
            print("📝 Final Notes:\n", notes)

        elif file_type == "mp3":
            print("🎧 Input is already MP3, renaming...")
            os.rename(input_file_path, output_file_path)

            print("📝 Transcribing...")
            transcript = transcription.transcribe_audio(output_file_path)
            print("📝 Transcript:\n", transcript)

        elif file_type == "pdf":
            print("📄 Converting PDF to notes...")
            slide_notes = slides.parse_generate_pdf(input_file_path)
            print("📑 Slide Notes:\n", slide_notes)

        else:
            return "Unsupported file type", 400

        return render_template(
            "processing.html",
            transcript=transcript,
            slide_notes=slide_notes
        )

    except ffmpeg.Error as e:
        print("❌ FFmpeg failed!")
        print("stdout:", e.stdout.decode("utf8"))
        print("stderr:", e.stderr.decode("utf8"))
        return "FFmpeg error occurred. See logs.", 500

