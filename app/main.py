import time
import arrow
import random
import psutil
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.models import VisitLog
from app.db import initialize_db, get_db, SessionLocal
from app.utils import log_visitor, paginate
from app.middleware import add_user_info_and_logging_middleware
from app.data.changes import CHANGES
from app.data.recipes import RECIPES
from app.data.quotes import QUOTES
from app.data.videos import VIDEOS
from app.data.coding_problems import CODING_PROBLEMS


# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize database
initialize_db()

# In-memory data
ip_to_info_map = {}

# Middleware
app.middleware("http")(
    add_user_info_and_logging_middleware(ip_to_info_map, log_visitor, SessionLocal)
)


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/updates", response_class=HTMLResponse)
async def updates(request: Request):
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": CHANGES,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
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
        visitor_name = log.visitor_name
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
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/recipes", response_class=HTMLResponse)
async def recipes(request: Request):
    return templates.TemplateResponse(
        "recipes.html",
        {
            "request": request,
            "recipes": RECIPES,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
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
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/server-status", response_class=HTMLResponse)
async def server_status(request: Request):
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

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
    }
    return templates.TemplateResponse(
        "server_status.html",
        {
            "request": request,
            "status": status,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/videos", response_class=HTMLResponse)
async def videos(request: Request):
    return templates.TemplateResponse(
        "videos.html",
        {
            "request": request,
            "videos": VIDEOS,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )


@app.get("/code", response_class=HTMLResponse)
async def code(request: Request):
    return templates.TemplateResponse(
        "code.html",
        {
            "request": request,
            "coding_problems": CODING_PROBLEMS,
            "visitor_name": request.state.visitor_name,
            "theme": request.state.theme,
        },
    )
