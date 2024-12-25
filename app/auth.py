import os
from fastapi import APIRouter, Request
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.db import get_db
from app.utils import get_or_create_user


router = APIRouter()

config = Config(".env")  # Reads from your .env
oauth = OAuth(config)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "email profile"},  # no "openid" here
    timeout=60,
)


@router.get("/signup")
async def signup(request: Request):
    # Redirect user to Google for login
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI"
    )  # e.g. http://127.0.0.1:8000/auth/google/callback
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", response_class=HTMLResponse)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await google.authorize_access_token(request)
    resp = await google.get("userinfo", token=token)
    user_info = resp.json()

    # Get or create user in the database
    user = get_or_create_user(db, email=user_info["email"], name=user_info.get("name"))

    # Save user details in the session
    request.session["user_id"] = user.id
    request.session["visitor_name"] = user.name

    content = f"""
    <h1>Google Login Successful!</h1>
    <pre>{user_info}</pre>
    <a href="/">Back to Home</a>
    """
    return HTMLResponse(content=content)
