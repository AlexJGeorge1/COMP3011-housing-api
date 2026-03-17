from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class RegionBase(BaseModel):
    """Base schema for a region's economic data."""
    name: str = Field(..., description="Region name", examples=["London"])
    ons_code: str = Field(..., description="ONS area code", examples=["E12000007"])
    median_salary: Optional[float] = Field(None, description="Median salary in GBP/year from ONS ASHE", examples=[45000.0])
    median_rent: Optional[float] = Field(None, description="Median rent in GBP/month from ONS PRS", examples=[1800.0])
    year: int = Field(..., description="Data year", examples=[2023])

class RegionCreate(RegionBase):
    """Schema for creating a new region record."""
    pass

class RegionUpdate(BaseModel):
    """Schema for updating an existing region record."""
    name: Optional[str] = Field(None, description="Region name", examples=["London"])
    ons_code: Optional[str] = Field(None, description="ONS area code", examples=["E12000007"])
    median_salary: Optional[float] = Field(None, description="Median salary in GBP/year from ONS ASHE", examples=[46000.0])
    median_rent: Optional[float] = Field(None, description="Median rent in GBP/month from ONS PRS", examples=[1850.0])
    year: Optional[int] = Field(None, description="Data year", examples=[2024])

class RegionResponse(RegionBase):
    """Schema for returning a region record."""
    id: str = Field(..., description="Unique identifier for the region record", examples=["550e8400-e29b-41d4-a716-446655440000"])
    
    model_config = ConfigDict(from_attributes=True)
