from flask import Blueprint, redirect, url_for, session
from services.auth_config import auth0
import os

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.getenv("AUTH0_CALLBACK_URL")
    )


@auth_bp.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    
    # ✅ Make a request to the Auth0 userinfo endpoint with token included
    resp = auth0.get(f'https://{os.getenv("AUTH0_DOMAIN")}/userinfo')
    user_info = resp.json()

    session["user"] = {
        "user_id": user_info["sub"],
        "name": user_info["name"],
        "email": user_info["email"],
    }
    return redirect(url_for("index"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?' +
        f'returnTo={url_for("index", _external=True)}&' +
        f'client_id={os.getenv("AUTH0_CLIENT_ID")}'
    )

@auth_bp.route("/signup")
def signup():
    return auth0.authorize_redirect(
        redirect_uri=os.getenv("AUTH0_CALLBACK_URL"),
        screen_hint="signup"  # 👈 this opens the sign-up tab first
    )
