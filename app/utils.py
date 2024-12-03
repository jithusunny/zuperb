import hashlib
from user_agents import parse
from app.models import VisitLog

ADJECTIVES = ["Witty", "Cheeky", "Bouncy", "Sassy", "Jolly", "Nifty"]
NOUNS = ["Penguin", "Unicorn", "Sloth", "Llama", "Otter", "Taco"]

def log_visitor(request, db, page):
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent_str = request.headers.get("User-Agent", "Unknown")
    referrer = request.headers.get("Referer", "Direct")

    # Parse user agent
    user_agent = parse(user_agent_str)
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

def generate_funny_name(ip):
    hash_value = int(hashlib.md5(ip.encode()).hexdigest(), 16)
    adjective = ADJECTIVES[hash_value % len(ADJECTIVES)]
    noun = NOUNS[hash_value % len(NOUNS)]
    return f"{adjective} {noun}"

def paginate(query, page, per_page):
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()
    next_page = page + 1 if len(items) == per_page else None
    previous_page = page - 1 if page > 1 else None
    return items, next_page, previous_page
