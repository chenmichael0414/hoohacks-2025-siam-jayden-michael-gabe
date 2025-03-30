import os
import ffmpeg
from flask import session, Blueprint, render_template, current_app, jsonify, redirect, url_for
import threading
import shutil
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
    filename = session.get("filename")
    file_type = session.get("file_type")
    input_file_path = session.get("file_path")

    if not filename or not input_file_path:
        return jsonify({"error": "Missing file information"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    thread = threading.Thread(
        target=process_file,
        args=(filename, file_type, input_file_path, upload_folder)
    )
    thread.start()

    return jsonify({"status": "processing started"}), 200


def process_file(filename, file_type, input_file_path, upload_folder):
    output_file_path = os.path.join(upload_folder, filename)

    if not input_file_path or not os.path.exists(input_file_path):
        print("🚫 Invalid input file path")
        return

    try:
        transcript = ""
        slide_notes = ""

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

        elif file_type in ["mp3"]:
            print("✅ Audio ready at:", output_file_path)
            print("📢 Transcribing...")
            transcript = transcription.transcribe_audio(output_file_path)
            print("📝 Transcript:\n", transcript)

        elif file_type == "pdf":
            print("📄 Converting PDF to notes...")
            slide_notes = slides.parse_generate_pdf(input_file_path)
            print("📑 Slide Notes:\n", slide_notes)
    
        else:
            print("❌ Unsupported file type")
            return

        # You can't return render_template here because it's running outside the Flask request context
        # You may want to instead save results to a file or database


        print("✅ Processing complete.")
        uploads_path = os.path.join(os.getcwd(), "uploads")

        if os.path.exists(uploads_path):
            shutil.rmtree(uploads_path)
            print("Uploads folder deleted.")
        else:
            print("Uploads folder does not exist.")

        frames_path = os.path.join(os.getcwd(), "frames")

        if os.path.exists(frames_path):
            shutil.rmtree(frames_path)
            print("frames folder deleted.")
        else:
            print("frames folder does not exist.")
    except ffmpeg.Error as e:
        print("❌ FFmpeg failed!")
        print("stdout:", e.stdout.decode("utf8"))
        print("stderr:", e.stderr.decode("utf8"))

    
      # ✅ At the end of process_file
        from models import db, LectureNote, User
        from flask_login import current_user

        pdf_path = os.path.join(upload_folder, "lecture_notes.pdf")
        
        if os.path.exists(pdf_path):
            print(f"📦 Saving {pdf_path} to DB...")

            note = LectureNote(
                filename="lecture_notes.pdf",
                file_path=pdf_path,
                user_id=current_user.id if hasattr(current_user, "id") else None
            )

            db.session.add(note)
            db.session.commit()
            print("✅ PDF saved to database.")

    except Exception as e:
        print("❌ Exception during processing:", str(e))