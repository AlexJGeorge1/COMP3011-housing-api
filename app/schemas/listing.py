from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List

class ListingBase(BaseModel):
    address: str = Field(..., description="Full property address")
    region: str = Field(..., description="ONS region name")
    price: int = Field(..., description="Sale price in GBP")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    property_type: Optional[str] = Field(None, description="e.g. detached, semi, terraced, flat")
    transaction_date: date = Field(..., description="Date the transaction completed")

class ListingCreate(ListingBase):
    pass

class ListingUpdate(BaseModel):
    address: Optional[str] = None
    region: Optional[str] = None
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    property_type: Optional[str] = None
    transaction_date: Optional[date] = None

class ListingResponse(ListingBase):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
