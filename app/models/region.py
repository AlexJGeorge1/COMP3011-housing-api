from sqlalchemy import Column, Integer, String, Float
import uuid

from app.database import Base

class Region(Base):
    """
    SQLAlchemy model representing an ONS region's economic data.
    
    Stores aggregated data for a specific geographic region, such as median salary
    and median rent for a given year. Used for affordability and trend analysis.
    """
    __tablename__ = "regions"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String, unique=True, index=True, nullable=False)
    ons_code = Column(String, unique=True, index=True, nullable=False)
    
    # Store aggregated figures
    median_salary = Column(Float, nullable=True)
    median_rent = Column(Float, nullable=True)
    year = Column(Integer, nullable=False)
