from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class VisitLog(Base):
    __tablename__ = "visit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String)
    timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    page = Column(String)
    url = Column(Text)
    referrer = Column(Text, default="Direct")
    user_agent = Column(Text)
    device_type = Column(String)
    browser = Column(String)
    operating_system = Column(String)
    visitor_name = Column(String)
    theme_id = Column(Integer, default=0)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone_number = Column(String, unique=True, nullable=True)
    login_method = Column(String, nullable=False)  # e.g., 'google', 'email', 'otp'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
