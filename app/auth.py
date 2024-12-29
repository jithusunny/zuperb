import os
import logging
from fastapi import APIRouter, Request
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.db import get_db
from app.utils import get_or_create_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@router.get("/login/google")
async def signup(request: Request):
    next_url = request.query_params.get("next", "/")
    request.session["next_url"] = next_url  # Save the next URL in the session

    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    logger.info(f"Initiating Google OAuth2 flow. Next URL: {next_url}")

    return await google.authorize_redirect(
        request, redirect_uri, prompt="select_account"
    )


@router.get("/auth/google/callback", response_class=HTMLResponse)
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle the Google OAuth2 callback, authenticate the user, and store session details.
    """
    try:
        # Log the state received in the callback
        state_in_request = request.query_params.get("state")
        logger.info(f"State received in callback: {state_in_request}")

        # Authorize the user and fetch token
        token = await google.authorize_access_token(request)
        resp = await google.get("userinfo", token=token)
        user_info = resp.json()

        logger.info(f"User info received: {user_info}")

        # Get or create the user in the database
        user = get_or_create_user(
            request=request,
            db=db,
            email=user_info.get("email"),
            name=user_info.get("name"),
        )

        # Store user information in the session
        request.session["user_id"] = str(user.id)
        request.session["visitor_name"] = user.name
        request.session["user_type"] = "authenticated"

        # Redirect back to the original page or default to home
        next_url = request.session.pop("next_url", "/")  # Fallback to home

        logger.info(f"Redirecting to: {next_url}")

        return RedirectResponse(next_url)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in Google callback: {e}")
        return PlainTextResponse("Authentication Failed", status_code=400)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
