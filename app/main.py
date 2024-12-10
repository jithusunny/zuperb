import os
import time
import arrow
import random
import psutil
from datetime import datetime
from dotenv import load_dotenv

from app.data.quotes import QUOTES
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import sessionmaker
from app.models import Base, VisitLog
from app.utils import log_visitor, generate_funny_name, paginate
from app.data.changes import CHANGES
from app.data.recipes import RECIPES

load_dotenv()

from sqlalchemy import create_engine

# Initialize FastAPI, Jinja2
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

ip_to_name_map = {}

def load_existing_mappings():
    db = SessionLocal()
    try:
        # Get all distinct IPs with their latest visitor_name from the logs
        logs = db.query(VisitLog.ip, VisitLog.visitor_name).distinct(VisitLog.ip).all()
        for ip, visitor_name in logs:
            if visitor_name:
                ip_to_name_map[ip] = visitor_name
    finally:
        db.close()

load_existing_mappings()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db=Depends(get_db)):
    #Do this in a middleware or something
    log_visitor(request, db, page="Home", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "visitor_name": name
        },
    )

@app.get("/updates", response_class=HTMLResponse)
async def updates(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Updates", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": CHANGES,
            "visitor_name": name
        },
    )

@app.get("/stats", response_class=HTMLResponse)
def stats(request: Request, db=Depends(get_db), page: int = 1):
    log_visitor(request, db, page="Visitors", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]

    per_page = 10
    logs, next_page, previous_page = paginate(
        db.query(VisitLog).order_by(VisitLog.timestamp.desc()), page, per_page
    )

    current_user_ip = request.headers.get("X-Forwarded-For", request.client.host)

    log_data = []
    for log in logs:
        visitor_name = log.visitor_name
        if log.ip == current_user_ip:
            visitor_name = f"{visitor_name} (You)"
        
        log_data.append({
            "funny_name": visitor_name,
            "when": arrow.get(log.timestamp).humanize(),
            "page_visited": log.page,
            "device": log.device_type,
        })

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "log_data": log_data,
            "next_page": next_page,
            "previous_page": previous_page,
            "visitor_name": name,
        },
    )

@app.get("/recipes", response_class=HTMLResponse)
async def recipes(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Recipes", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]    
    
    return templates.TemplateResponse("recipes.html", {"request": request, "recipes": RECIPES, "visitor_name": name})

@app.get("/quotes", response_class=HTMLResponse)
async def quotes(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Quotes", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]    

    random_quote = random.choice(QUOTES)
    return templates.TemplateResponse("quotes.html", {"request": request, "quote": random_quote, "visitor_name": name,})

@app.get("/server-status", response_class=HTMLResponse)
async def server_status(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Status", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]    

    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_hours = int(uptime_seconds // 3600)

    start_time_formatted = datetime.fromtimestamp(boot_time).strftime("%b %d, %I:%M %p")

    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_used = int(memory.used / (1024**2))
    memory_total = int(memory.total / (1024**2))
    disk = psutil.disk_usage('/')
    disk_total = disk.total / (1024**3)
    disk_used = disk.used / (1024**3)

    status = {
        "uptime_hours": uptime_hours,
        "start_time_formatted": start_time_formatted,
        "cpu_usage": f"{cpu_usage:.1f}",
        "memory_total": memory_total,
        "memory_used": memory_used,
        "disk_total": f"{disk_total:.1f}",
        "disk_used": f"{disk_used:.1f}",
    }

    return templates.TemplateResponse("server_status.html", {"request": request, "status": status, "visitor_name": name,})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="About", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]    
    return templates.TemplateResponse("about.html", {"request": request, "visitor_name": name,})

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="History", ip_to_name_map=ip_to_name_map)
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    name = ip_to_name_map[ip]    
    return templates.TemplateResponse("history.html", {"request": request, "visitor_name": name,})