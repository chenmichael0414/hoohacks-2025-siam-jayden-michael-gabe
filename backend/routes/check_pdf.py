import os
from flask import Blueprint, jsonify, current_app

check_pdf_bp = Blueprint("check_pdf", __name__)

@check_pdf_bp.route("/check_pdf/<filename>")
def check_pdf(filename):
    exists = os.path.exists(filename)
    return jsonify({"exists": exists})