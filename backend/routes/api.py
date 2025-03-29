from flask import Blueprint, jsonify, request
import requests

api_bp = Blueprint("api", __name__)

SIS_BASE_URL = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"

@api_bp.route("/courses/<subject>", methods=["GET"])
def get_courses(subject):
    term = request.args.get("term", "1252")  # default Fall 2023
    subject = subject.upper()

    url = f"{SIS_BASE_URL}&term={term}&subject={subject}&page=1"
    
    try:
        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500