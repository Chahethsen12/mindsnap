from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Snap(Base):
    __tablename__ = "snaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    content_type = Column(String, nullable=True)  # article, code, design, product, etc.
    source_url = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # comma-separated e.g. "python,backend,tutorial"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="snaps")

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzczMTQ3MzExfQ.rgNyFWH8da6yeVkSKcFo5ApaLoANb7BZyIZL8wyAP6o