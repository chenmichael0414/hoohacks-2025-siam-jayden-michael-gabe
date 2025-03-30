import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app
from services import transcription, slides, powerpoint, video

process_bp = Blueprint("process", __name__)


@process_bp.route("/processing")
def processing_page():
    filename = session.get('filename')
    if not filename:
        return "No file found in session", 400

    return render_template("processing.html", filename=filename)



@process_bp.route("/start_processing", methods=["POST"])
def start_processing():
    filename = session.get('filename')
    if not filename:
        return jsonify({"error": "No file found in session"}), 400

    
    thread = threading.Thread(target=process_file, args=(filename,))
    thread.start()


def process_file(filename):
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

        elif file_type == "pdf":
            print("📄 Converting PDF to text using OCR...")
            notes = slides.parse_generate_pdf(input_file_path)
            print("📝 Notes:\n", notes)
        elif file_type == "pptx":
            print("🎨 Detecting slides from PowerPoint...")
            slides_text = powerpoint.detect_and_write_slides_from_pptx(input_file_path)
            print("📝 Slides:\n", slides_text)
        else:
            return "Unsupported file type", 400
        if file_type == "mp4" or file_type == "mov" or file_type == "mp3":
            print("✅ Audio ready at:", output_file_path)
            print("📢 Transcribing...")
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

