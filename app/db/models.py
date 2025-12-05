# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import func
from sqlalchemy.types import JSON
from app.db.base import Base

# Note: SQLite's native JSON support depends on version; SQLAlchemy will store JSON as TEXT if needed.
class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    config = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
