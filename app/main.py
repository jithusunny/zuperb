import arrow
import hashlib
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from user_agents import parse
from app.data.changes import CHANGES

# Initialize FastAPI and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Database setup
DATABASE_URL = "sqlite:///./zuperb.db"  # Updated to reflect the new database file name
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database tables
class Hits(Base):
    __tablename__ = "hits"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)

class VisitLog(Base):
    __tablename__ = "visit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    page = Column(String)
    url = Column(Text)
    referrer = Column(Text, default="Direct")
    user_agent = Column(Text)
    device_type = Column(String)
    browser = Column(String)
    operating_system = Column(String)

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Increment hits in the database
def increment_hits(db):
    hit_record = db.query(Hits).first()
    if not hit_record:
        hit_record = Hits(count=1)
        db.add(hit_record)
    else:
        hit_record.count += 1
    db.commit()
    return hit_record.count

# Utility: Log Visitor Data
def log_visitor(request: Request, db, page: str):
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent_str = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")

    # Parse user agent
    user_agent = parse(user_agent_str)

    # Detect device type
    device_type = (
        "Mobile" if user_agent.is_mobile else
        "Tablet" if user_agent.is_tablet else
        "Desktop"
    )
    browser = user_agent.browser.family or "Unknown"
    operating_system = user_agent.os.family or "Unknown"

    # Create log entry
    visit_log = VisitLog(
        ip=ip,
        page=page,
        url=str(request.url),
        referrer=referrer,
        user_agent=user_agent_str,
        device_type=device_type,
        browser=browser,
        operating_system=operating_system,
    )
    db.add(visit_log)
    db.commit()

# List of funny adjectives and nouns
ADJECTIVES = ["Witty", "Cheeky", "Bouncy", "Sassy", "Jolly", "Nifty"]
NOUNS = ["Penguin", "Unicorn", "Sloth", "Llama", "Otter", "Taco"]

def generate_funny_name(ip: str) -> str:
    """Generate a unique funny name based on the IP."""
    hash_value = int(hashlib.md5(ip.encode()).hexdigest(), 16)
    adjective = ADJECTIVES[hash_value % len(ADJECTIVES)]
    noun = NOUNS[hash_value % len(NOUNS)]
    return f"{adjective} {noun}"

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db=Depends(get_db)):
    hits = increment_hits(db)
    log_visitor(request, db, page="Home")
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "quote": "We suffer more often in imagination than in reality.",
            "author": "Seneca",
            "hits": hits,
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
    per_page = 10
    offset = (page - 1) * per_page
    logs = db.query(VisitLog).order_by(VisitLog.timestamp.desc()).offset(offset).limit(per_page).all()

    print(logs[0].referrer)
    # Convert IPs to funny names
    log_data = [
        {
            "funny_name": generate_funny_name(log.ip),
            "when": arrow.get(log.timestamp).humanize(),
            "page_visited": log.page,
            "device": log.device_type,
        }
        for log in logs
    ]
    next_page = page + 1 if len(logs) == per_page else None
    previous_page = page - 1 if page > 1 else None

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "log_data": log_data,
            "next_page": next_page,
            "previous_page": previous_page,
        },
    )
