from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List

class ListingBase(BaseModel):
    """Base schema for a property listing."""
    address: str = Field(..., description="Full property address", examples=["10 Downing Street, London"])
    region: str = Field(..., description="ONS region name", examples=["London"])
    price: int = Field(..., description="Sale price in GBP", examples=[1500000])
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms", examples=[3])
    property_type: Optional[str] = Field(None, description="e.g. detached, semi, terraced, flat", examples=["terraced"])
    transaction_date: date = Field(..., description="Date the transaction completed", examples=["2024-01-15"])

class ListingCreate(ListingBase):
    """Schema for creating a new property listing."""
    pass

class ListingUpdate(BaseModel):
    """Schema for updating an existing property listing. All fields are optional."""
    address: Optional[str] = Field(None, description="Full property address", examples=["10 Downing Street, London"])
    region: Optional[str] = Field(None, description="ONS region name", examples=["London"])
    price: Optional[int] = Field(None, description="Sale price in GBP", examples=[1550000])
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms", examples=[4])
    property_type: Optional[str] = Field(None, description="e.g. detached, semi, terraced, flat", examples=["terraced"])
    transaction_date: Optional[date] = Field(None, description="Date the transaction completed", examples=["2024-02-20"])

class ListingResponse(ListingBase):
    """Schema for returning a property listing."""
    id: str = Field(..., description="Unique identifier for the listing", examples=["123e4567-e89b-12d3-a456-426614174000"])
    created_at: datetime = Field(..., description="Timestamp of when the listing was created", examples=["2024-03-01T12:00:00Z"])
    
    model_config = ConfigDict(from_attributes=True)
