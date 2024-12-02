from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.data.changes import ALL_CHANGES
import os

# Initialize FastAPI and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Load environment variables
HITS_FILE = os.getenv("HITS_FILE", "hits.txt")

# Ensure hits file exists
if not os.path.exists(HITS_FILE):
    with open(HITS_FILE, "w") as f:
        f.write("0")

# Increment hit count
def increment_hits():
    with open(HITS_FILE, "r+") as f:
        count = int(f.read().strip())
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    hits = increment_hits()
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "quote": "A man sees in the world what he carries in his heart",
            "author": "Von Goethe",
            "hits": hits,
        },
    )

@app.get("/updates", response_class=HTMLResponse)
def updates(request: Request):
    return templates.TemplateResponse(
        "updates.html",
        {
            "request": request,
            "updates": ALL_CHANGES,
        },
    )
