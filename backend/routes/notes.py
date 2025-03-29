from flask import Blueprint, request, jsonify
from db.db import notes_collection
from datetime import datetime, timezone

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/notes", methods=["POST"])
def save_notes():
    data = request.get_json()

    required_fields = ["user_id", "course", "video", "notes"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_note = {
        "user_id": data["user_id"],
        "course": data["course"],
        "video": data["video"],
        "notes": data["notes"],
        "created_at": datetime.now(timezone.utc)
    }

    result = notes_collection.insert_one(new_note)
    return jsonify({"message": "Notes saved", "note_id": str(result.inserted_id)}), 201


@notes_bp.route("/notes/<user_id>", methods=["GET"])
def get_notes_for_user(user_id):
    user_notes = list(notes_collection.find({"user_id": user_id}))
    for note in user_notes:
        note["_id"] = str(note["_id"])  # Convert ObjectId to string for JSON
    return jsonify(user_notes)


@notes_bp.route("/notes/<user_id>/<course>", methods=["GET"])
def get_notes_for_course(user_id, course):
    course_notes = list(notes_collection.find({"user_id": user_id, "course": course}))
    for note in course_notes:
        note["_id"] = str(note["_id"])
    return jsonify(course_notes)
