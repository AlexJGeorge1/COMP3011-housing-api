from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.sql import func
import uuid

from app.database import Base

try:
    from pgvector.sqlalchemy import Vector
    _vector_type = Vector(384)
except Exception:
    _vector_type = None


class Listing(Base):
    __tablename__ = "listings"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    address = Column(String, index=True, nullable=False)
    region = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True)  # detached, semi, terraced, flat
    transaction_date = Column(Date, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # pgvector embedding column for semantic search (skipped if pgvector unavailable)
    if _vector_type is not None:
        embedding = Column(_vector_type, nullable=True)
