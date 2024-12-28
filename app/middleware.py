import time

# from app.data.themes import THEMES

from app.utils import log_visitor

# Track online users
online_users = {}
SESSION_TIMEOUT = 300  # 5 minutes of inactivity considered offline


def cleanup_online_users():
    """Remove users inactive for more than SESSION_TIMEOUT seconds."""
    current_time = time.time()
    inactive_users = [
        user_id
        for user_id, last_active in online_users.items()
        if current_time - last_active > SESSION_TIMEOUT
    ]
    for user_id in inactive_users:
        del online_users[user_id]


def user_tracking_middleware(get_db):
    """Middleware to track authenticated users, log visits, and manage online users."""

    async def middleware(request, call_next):
        db = next(get_db())
        try:
            # Call the next middleware and get the response
            response = await call_next(request)

            # Check if user is authenticated
            user_id = request.session.get("user_id")
            if user_id:
                # Log the visit
                log_visitor(request, db, user_id=user_id)

                # Track the user as online
                online_users[user_id] = time.time()

                # Cleanup inactive users
                cleanup_online_users()

            return response
        finally:
            db.close()

    return middleware
