import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app
from services import transcription, slides

process_bp = Blueprint("process", __name__)


def get_audio_duration(path):
    try:
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return round(duration, 2)
    except Exception as e:
        print("Could not get duration:", e)
        return None

@process_bp.route("/processing")
def processing_page():
    filename = session.get("filename")
    if not filename:
        return "No file uploaded", 400

    file_type = session.get("file_type")
    input_file_path = session.get("file_path")
    output_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_to_audio.mp3")
    output_video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "lecture_video.mp4")

    print("📼 Original file:", input_file_path)
    print("📼 Original duration:", get_audio_duration(input_file_path))

    try:
        if file_type in ["mp4", "mov"]:
            (
                ffmpeg
                .input(input_file_path)
                .output(output_file_path, format="mp3", audio_bitrate="128k")
                .run(capture_stdout=True, capture_stderr=True)
            )
        elif file_type == "mp3":
            os.replace(input_file_path, output_file_path)
        elif file_type == "pdf":
            print("📄 Converting PDF to text using OCR...")
            notes = slides.parse_generate_pdf(input_file_path)
            print("📝 Notes:\n", notes)
        else:
            return "Unsupported file type", 400

        print("🎧 Output audio saved to:", output_file_path)
        print("🎧 Output duration:", get_audio_duration(output_file_path))

        # Send to transcription
        transcript = transcription.transcribe_audio(output_file_path)
        print("📝 Transcript:\n", transcript)

        return render_template("processing.html")

    except ffmpeg.Error as e:
        print("⚠️ FFmpeg error:", e.stderr.decode())
        return "Audio processing failed", 500
