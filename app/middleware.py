from fastapi import Request
from app.data.themes import THEMES

def add_user_info_and_logging_middleware(ip_to_info_map, log_visitor, db_session):
    async def middleware(request: Request, call_next):
        db = db_session()
        try:
            log_visitor(request, db, page=request.url.path, ip_to_info_map=ip_to_info_map)
            ip = request.headers.get("X-Forwarded-For", request.client.host)
            user_info = ip_to_info_map.get(ip, {"name": "Guest", "theme": 0})
            request.state.visitor_name = user_info["name"]
            request.state.theme = THEMES[user_info["theme"]]
        finally:
            db.close()

        response = await call_next(request)
        return response

    return middleware
