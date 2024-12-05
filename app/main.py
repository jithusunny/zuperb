import arrow
import random
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

from sqlalchemy import create_engine

# Initialize FastAPI, Jinja2
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Database setup
DATABASE_URL = "sqlite:///./zuperb.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

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
    log_visitor(request, db, page="Home")
    random_quote = random.choice(QUOTES)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "quote": random_quote["quote"],
            "author": random_quote["author"],
        },
    )

@app.get("/updates", response_class=HTMLResponse)
async def updates(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Updates")
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": CHANGES,
        },
    )

@app.get("/stats", response_class=HTMLResponse)
def stats(request: Request, db=Depends(get_db), page: int = 1):
    log_visitor(request, db, page="Visitors")
    per_page = 10
    logs, next_page, previous_page = paginate(
        db.query(VisitLog).order_by(VisitLog.timestamp.desc()), page, per_page
    )
    log_data = [
        {
            "funny_name": generate_funny_name(log.ip),
            "when": arrow.get(log.timestamp).humanize(),
            "page_visited": log.page,
            "device": log.device_type,
        }
        for log in logs
    ]
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "log_data": log_data,
            "next_page": next_page,
            "previous_page": previous_page,
        },
    )

@app.get("/recipes", response_class=HTMLResponse)
async def recipes(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Recipes")
    return templates.TemplateResponse("recipes.html", {"request": request, "recipes": RECIPES})

@app.get("/quotes", response_class=HTMLResponse)
async def quotes(request: Request, db=Depends(get_db)):
    log_visitor(request, db, page="Quotes")
    random_quote = random.choice(QUOTES)
    return templates.TemplateResponse("quotes.html", {"request": request, "quote": random_quote})