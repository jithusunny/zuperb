import os
import time
import arrow
import random
import psutil
import bleach
import markdown
from uuid import UUID
from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import VisitLog, Note
from sqlalchemy.orm import Session
from app.utils import paginate, take_screenshots
from app.middleware import (
    online_users,
    cleanup_online_users,
    user_tracking_middleware,
)
from app.db import get_db
from app.data.changes import CHANGES
from app.data.recipes import RECIPES
from app.data.quotes import QUOTES
from app.data.videos import VIDEOS
from app.data.projects import PROJECTS
from app.data.coding_problems import CODING_PROBLEMS
from app.auth import router as auth_router

# Initialize FastAPI
app = FastAPI()

# Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=user_tracking_middleware(get_db))

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
        },
    )


@app.get("/updates", response_class=HTMLResponse)
async def updates(request: Request):
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": CHANGES,
        },
    )


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request, db=Depends(get_db), page: int = 1):
    # Fetch paginated logs
    logs_data = paginate(
        db.query(VisitLog).order_by(VisitLog.timestamp.desc()), page, per_page=10
    )
    current_user_ip = request.headers.get("X-Forwarded-For", request.client.host)

    # Process logs into a format suitable for the template
    log_data = []
    for log in logs_data["items"]:
        user = log.user
        if user and user.name:  # Check if the user is a real user
            visitor_name = " ".join(
                part[0].upper() for part in user.name.split() if part
            )
        else:
            visitor_name = "Guest"

        if log.ip == current_user_ip:
            visitor_name = f"{visitor_name} (You)"

        log_data.append(
            {
                "visitor_name": visitor_name,
                "when": arrow.get(log.timestamp).humanize(),
                "page_visited": log.page,
                "device": log.device_type,
            }
        )

    # Render template with processed data
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "log_data": log_data,
            "next_page": logs_data["next_page"],
            "previous_page": logs_data["previous_page"],
        },
    )


@app.get("/projects", response_class=HTMLResponse)
async def get_projects_list(request: Request):
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "projects": PROJECTS,
        },
    )


@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def get_project_detail(request: Request, project_id: int):
    project = next(
        (project for project in PROJECTS if project["id"] == project_id), None
    )
    return templates.TemplateResponse(
        "project.html",
        {
            "request": request,
            "project": project,
        },
    )


@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes_list(request: Request):
    return templates.TemplateResponse(
        "recipes.html",
        {
            "request": request,
            "recipes": RECIPES,
        },
    )


@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
async def get_recipe_detail(request: Request, recipe_id: int):
    recipe = next((recipe for recipe in RECIPES if recipe["id"] == recipe_id), None)
    return templates.TemplateResponse(
        "recipe.html",
        {
            "request": request,
            "recipe": recipe,
        },
    )


@app.get("/quotes", response_class=HTMLResponse)
async def quotes(request: Request):
    random_quote = random.choice(QUOTES)
    return templates.TemplateResponse(
        "quotes.html",
        {
            "request": request,
            "quote": random_quote,
        },
    )


@app.get("/server-status", response_class=HTMLResponse)
async def server_status(request: Request):
    """Fetch and display server status."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    process = psutil.Process()  # Get the current process

    # Perform cleanup to ensure the online user count is accurate
    cleanup_online_users()

    # Fetch server status and online users
    status = {
        "uptime_hours": int(uptime_seconds // 3600),
        "start_time_formatted": datetime.fromtimestamp(boot_time).strftime(
            "%b %d, %I:%M %p"
        ),
        "cpu_usage": f"{psutil.cpu_percent(interval=1):.1f}",
        "memory_used": int(memory.used / (1024**2)),
        "memory_total": int(memory.total / (1024**2)),
        "disk_used": f"{disk.used / (1024**3):.1f}",
        "disk_total": f"{disk.total / (1024**3):.1f}",
        "online_users": len(online_users),
        "app_memory": f"{process.memory_info().rss / (1024**2):.2f}",  # Memory in MB
    }

    return templates.TemplateResponse(
        "server_status.html",
        {
            "request": request,
            "status": status,
        },
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
        },
    )


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
        },
    )


@app.get("/videos", response_class=HTMLResponse)
async def videos(request: Request):
    return templates.TemplateResponse(
        "videos.html",
        {
            "request": request,
            "videos": VIDEOS,
        },
    )


@app.get("/videos/{video_id}", response_class=HTMLResponse)
async def video_detail(request: Request, video_id: int):
    video = next((v for v in VIDEOS if v["id"] == video_id), None)
    return templates.TemplateResponse(
        "video.html",
        {
            "request": request,
            "video": video,
        },
    )


@app.get("/code", response_class=HTMLResponse)
async def code(request: Request):
    return templates.TemplateResponse(
        "coding_problems.html",
        {
            "request": request,
            "coding_problems": CODING_PROBLEMS,
        },
    )


@app.get("/code/{problem_id}", response_class=HTMLResponse)
async def code_detail(request: Request, problem_id: int):
    problem = next((p for p in CODING_PROBLEMS if p["id"] == problem_id), None)
    return templates.TemplateResponse(
        "coding_problem.html",
        {
            "request": request,
            "problem": problem,
        },
    )


@app.get("/robots.txt", response_class=PlainTextResponse)
def serve_robots():
    file_path = os.path.join("app", "static", "robots.txt")
    with open(file_path, "r") as f:
        return f.read()


@app.get("/screenshots")
def run_screenshots(request: Request):
    if request.client.host != "127.0.0.1":
        return {"status": "not allowed"}

    take_screenshots()

    return {"status": "done"}


@app.get("/notes", response_class=HTMLResponse)
async def list_notes(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        # Handle unauthenticated user
        return RedirectResponse("/login/google?next=/notes", status_code=302)

    notes = (
        db.query(Note)
        .filter(Note.created_by == user_id)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "notes.html", {"request": request, "notes": notes}
    )


@app.get("/notes/new", response_class=HTMLResponse)
async def new_note_page(request: Request):
    return templates.TemplateResponse(
        "note_form.html", {"request": request, "note": None}
    )


@app.post("/notes/new")
async def create_note(
    request: Request,
    title: str = Form(""),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    new_note = Note(title=title, content=content, created_by=user_id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return RedirectResponse(f"/notes/{new_note.id}", status_code=302)


# Define allowed tags
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union(
    {
        "p",
        "pre",
        "span",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "img",
        "a",
        "ul",
        "ol",
        "li",
        "strong",
        "em",
        "code",
        "blockquote",
    }
)

# Define allowed attributes as a dictionary
ALLOWED_ATTRIBUTES = bleach.sanitizer.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update(
    {
        "a": ["href", "title", "target", "rel"],
        "img": ["src", "alt", "title"],
        "span": ["class"],
    }
)

# Optionally, define allowed protocols
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


@app.get("/notes/{note_id}", response_class=HTMLResponse)
async def view_note(note_id: UUID, request: Request, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        return PlainTextResponse("Note not found", status_code=404)

    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=["fenced_code", "codehilite"])
    note_html = md.convert(note.content)

    # Sanitize HTML
    note_html = bleach.clean(
        note_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )

    return templates.TemplateResponse(
        "note_preview.html",
        {"request": request, "note": note, "note_content_html": note_html},
    )


@app.get("/notes/{note_id}/edit", response_class=HTMLResponse)
async def edit_note_page(
    note_id: UUID, request: Request, db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        return PlainTextResponse("Note not found", status_code=404)

    return templates.TemplateResponse(
        "note_form.html", {"request": request, "note": note}
    )


@app.post("/notes/{note_id}/edit")
async def update_note(
    note_id: UUID,
    title: str = Form(""),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        return PlainTextResponse("Note not found", status_code=404)

    note.title = title
    note.content = content
    db.commit()
    return RedirectResponse(f"/notes/{note.id}", status_code=302)
