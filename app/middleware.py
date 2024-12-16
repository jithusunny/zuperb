import time
from app.data.themes import THEMES

# Track online users
online_users = {}
SESSION_TIMEOUT = 300  # 5 minutes of inactivity considered offline


def cleanup_online_users():
    """Remove users inactive for more than SESSION_TIMEOUT seconds."""
    current_time = time.time()
    inactive_ips = [
        ip
        for ip, last_active in online_users.items()
        if current_time - last_active > SESSION_TIMEOUT
    ]
    for ip in inactive_ips:
        del online_users[ip]


def add_user_info_and_logging_middleware(ip_to_info_map, log_visitor, db_session):
    async def middleware(request, call_next):
        db = db_session()
        try:
            # Log visitor activity
            log_visitor(
                request, db, page=request.url.path, ip_to_info_map=ip_to_info_map
            )

            # Track online users
            ip = request.headers.get("X-Forwarded-For", request.client.host)
            online_users[ip] = time.time()  # Update user activity timestamp

            # Cleanup inactive users
            cleanup_online_users()

            # Set visitor info in the request
            user_info = ip_to_info_map.get(ip, {"name": "Guest", "theme": 0})
            request.state.visitor_name = user_info["name"]
            request.state.theme = THEMES[user_info["theme"]]
        finally:
            db.close()

        response = await call_next(request)
        return response

    return middleware
