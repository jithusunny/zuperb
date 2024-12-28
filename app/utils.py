import os
import random
import hashlib
from user_agents import parse
from datetime import datetime
from app.models import VisitLog
from playwright.sync_api import sync_playwright
from app.data.themes import THEMES
from app.models import User
from sqlalchemy.orm import Session

BASE_URL = "http://127.0.0.1:8000"
CONFIG_PATHS_FOR_SCREENSHOT = [
    "/",
    "/updates",
    "/stats",
    "/recipes",
    "/quotes",
    "/server-status",
    "/about",
    "/history",
    "/videos",
    "/code",
]
SCREENSHOTS_OUTPUT_DIR = "/home/jisuka/zuperb_screenshots"

ADJECTIVES = [
    "Bright",
    "Gentle",
    "Brave",
    "Kind",
    "Bold",
    "Calm",
    "Happy",
    "Lively",
    "Jolly",
    "Graceful",
    "Radiant",
    "Cheerful",
    "Charming",
    "Elegant",
    "Joyful",
    "Peaceful",
    "Strong",
    "Sweet",
    "Magical",
    "Vibrant",
    "Loyal",
    "Splendid",
    "Brilliant",
    "Thoughtful",
    "Witty",
    "Fabulous",
    "Daring",
]

NOUNS = [
    "Dove",
    "Swan",
    "Eagle",
    "Hawk",
    "Raven",
    "Hummingbird",
    "Peacock",
    "Butterfly",
    "Phoenix",
    "Lion",
    "Tiger",
    "Panther",
    "Leopard",
    "Cheetah",
    "Otter",
    "Panda",
    "Deer",
    "Rabbit",
    "Stag",
    "Falcon",
    "Heron",
    "Crane",
    "Kite",
    "Bluebird",
    "Parrot",
    "Sparrow",
    "Lark",
    "Finch",
    "Robin",
    "Jay",
]


def generate_random_theme():
    return random.choice(list(THEMES.keys()))


def generate_funny_name(ip):
    hash_value = int(hashlib.md5(ip.encode()).hexdigest(), 16)
    return (
        f"{ADJECTIVES[hash_value % len(ADJECTIVES)]} {NOUNS[hash_value % len(NOUNS)]}"
    )


def parse_user_agent(user_agent):
    """Parse the User-Agent string to extract device type, operating system, and browser."""
    ua = parse(user_agent)
    device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "Desktop"
    operating_system = ua.os.family  # E.g., "Windows", "iOS", "Android"
    browser = ua.browser.family  # E.g., "Chrome", "Firefox", "Safari"
    return device_type, operating_system, browser


def log_visitor(request, db: Session, user_id: str):
    """Log visitor activity."""
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent_str = request.headers.get("User-Agent", "Unknown")
    device_type, operating_system, browser = parse_user_agent(user_agent_str)

    visit_log = VisitLog(
        user_id=user_id,
        page=request.url.path,
        url=str(request.url),
        referrer=request.headers.get("Referer", "Direct"),
        user_agent=user_agent_str,
        device_type=device_type,
        operating_system=operating_system,
        browser=browser,
        ip=ip,
    )
    db.add(visit_log)
    db.commit()


def get_or_create_user(request, db: Session, email: str, name: str):
    """Get or create a user based on email."""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()

    return user


def paginate(query, page, per_page):
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    return {
        "items": items,
        "next_page": page + 1 if len(items) == per_page else None,
        "previous_page": page - 1 if page > 1 else None,
    }


def take_screenshots():
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(SCREENSHOTS_OUTPUT_DIR, today_str)
    os.makedirs(output_dir, exist_ok=True)

    # Take screenshots for each configured path
    for path in CONFIG_PATHS_FOR_SCREENSHOT:
        name = path.strip("/")
        full_url = f"{BASE_URL}{path}"
        print("full_url is:", full_url)
        mobile_filename = f"{name}_mobile.png"
        laptop_filename = f"{name}_laptop.png"

        mobile_path = os.path.join(output_dir, mobile_filename)
        laptop_path = os.path.join(output_dir, laptop_filename)

        with sync_playwright() as p:
            browser = p.chromium.launch()

            # Mobile screenshot
            mobile_context = browser.new_context(
                viewport={"width": 375, "height": 667},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            )
            mobile_page = mobile_context.new_page()
            mobile_page.goto(full_url)
            mobile_page.screenshot(path=mobile_path, full_page=True)
            mobile_context.close()

            # Laptop screenshot
            laptop_context = browser.new_context(
                viewport={"width": 1366, "height": 768}
            )
            laptop_page = laptop_context.new_page()
            laptop_page.goto(full_url)
            laptop_page.screenshot(path=laptop_path, full_page=True)
            laptop_context.close()

            browser.close()
