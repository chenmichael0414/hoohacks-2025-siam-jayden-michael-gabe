import requests
from flask import session

SIS_BASE_URL = (
    "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/"
    "WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01"
)

def build_term_code(season, year):
    season = season.lower()
    suffix = "2" if season == "spring" else "8" if season == "fall" else None
    if suffix is None:
        return None
    return f"1{str(year)[-2:]}{suffix}"

def check_course_exists(subject, number, season, year):
    """
    Checks if a course exists in SIS. Returns (True, course_data) or (False, None)
    """
    term = build_term_code(season, year)
    if not term:
        return False, None

    subject = subject.upper()
    url = f"{SIS_BASE_URL}&term={term}&subject={subject}&catalog_nbr={number}&page=1"

    try:
        response = requests.get(url)
        data = response.json()
        if "classes" in data and data["classes"]:
            return True, {
                "subject": subject,
                "number": number,
            }
        else:
            return False, None
    except Exception as e:
        print(f"Error checking course: {e}")
        return False, None

def store_course_in_session(course_data):
    """
    Saves a course dictionary to the Flask session for later use.
    """
    session["course_match"] = course_data
