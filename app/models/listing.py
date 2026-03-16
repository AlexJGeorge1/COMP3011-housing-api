from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from app.database import Base

class Listing(Base):
    __tablename__ = "listings"

    # We use UUIDs (stored as strings in standard Postgres without the UUID type extension, or native UUID)
    # For simplicity across DB engines, storing as string is common, but Postgres supports native UUID well.
    # Using String for broad compatibility, storing hex.
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    address = Column(String, index=True, nullable=False)
    region = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=True)
    property_type = Column(String, nullable=True) # detached, semi, terraced, flat
    transaction_date = Column(Date, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # pgvector embedding column for semantic search
    embedding = Column(Vector(384), nullable=True)
