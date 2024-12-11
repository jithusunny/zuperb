import random
import hashlib
from user_agents import parse
from app.models import VisitLog
from app.data.themes import THEMES

ADJECTIVES = [
    "Bright", "Gentle", "Brave", "Kind", "Bold", "Calm", "Happy", "Lively", 
    "Jolly", "Graceful", "Radiant", "Cheerful", "Charming", "Elegant", 
    "Joyful", "Peaceful", "Strong", "Sweet", "Magical", "Vibrant", "Loyal", 
    "Splendid", "Brilliant", "Thoughtful", "Witty", "Fabulous", "Daring"
]

NOUNS = [
    "Dove", "Swan", "Eagle", "Hawk", "Raven", "Hummingbird", "Peacock", 
    "Butterfly", "Phoenix", "Lion", "Tiger", "Panther", "Leopard", "Cheetah", 
    "Otter", "Panda", "Deer", "Rabbit", "Stag", "Falcon", "Heron", "Crane", 
    "Kite", "Bluebird", "Parrot", "Sparrow", "Lark", "Finch", "Robin", "Jay"
]

def generate_random_theme():
    return random.choice(list(THEMES.keys()))

def generate_funny_name(ip):
    hash_value = int(hashlib.md5(ip.encode()).hexdigest(), 16)
    return f"{ADJECTIVES[hash_value % len(ADJECTIVES)]} {NOUNS[hash_value % len(NOUNS)]}"

def parse_device_type(user_agent_str):
    user_agent = parse(user_agent_str)
    if user_agent.is_mobile:
        return "Mobile"
    if user_agent.is_tablet:
        return "Tablet"
    return "Desktop"

def log_visitor(request, db, page, ip_to_info_map):
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent_str = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")
    user_info = ip_to_info_map.get(ip, {"name": generate_funny_name(ip), "theme": generate_random_theme()})
    ip_to_info_map[ip] = user_info

    visit_log = VisitLog(
        ip=ip,
        page=page,
        url=str(request.url),
        referrer=referrer,
        user_agent=user_agent_str,
        device_type=parse_device_type(user_agent_str),
        visitor_name=user_info["name"],
        theme_id=user_info["theme"],
    )
    db.add(visit_log)
    db.commit()

def paginate(query, page, per_page):
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    return {
        "items": items,
        "next_page": page + 1 if len(items) == per_page else None,
        "previous_page": page - 1 if page > 1 else None,
    }