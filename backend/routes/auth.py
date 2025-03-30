from flask import Blueprint, redirect, session, url_for, request
from services.auth_config import auth0
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@auth_bp.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    user_info = auth0.parse_id_token(token)
    session["user"] = {
        "user_id": user_info["sub"],
        "name": user_info["name"],
        "email": user_info["email"],
    }
    return redirect(url_for("index"))  # or wherever you want

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?returnTo=http://localhost:5000')
