from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.data.changes import CHANGES

# Initialize FastAPI and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Database setup
DATABASE_URL = "sqlite:///./hits.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database table for hit count
class Hits(Base):
    __tablename__ = "hits"
    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, default=0)

# Create the table if it doesn't exist
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

# Routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db=Depends(get_db)):
    hits = increment_hits(db)
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
def updates(request: Request):
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": CHANGES,
        },
    )
