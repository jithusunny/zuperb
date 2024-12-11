from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class VisitLog(Base):
    __tablename__ = "visit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    page = Column(String)
    url = Column(Text)
    referrer = Column(Text, default="Direct")
    user_agent = Column(Text)
    device_type = Column(String)
    browser = Column(String)
    operating_system = Column(String)
    visitor_name = Column(String)
    theme_id = Column(Integer, default=0)
