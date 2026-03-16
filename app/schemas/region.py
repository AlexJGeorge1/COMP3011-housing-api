from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class RegionBase(BaseModel):
    name: str = Field(..., description="Region name")
    ons_code: str = Field(..., description="ONS area code")
    median_salary: Optional[float] = Field(None, description="Median salary in GBP/year from ONS ASHE")
    median_rent: Optional[float] = Field(None, description="Median rent in GBP/month from ONS PRS")
    year: int = Field(..., description="Data year")

class RegionCreate(RegionBase):
    pass

class RegionUpdate(BaseModel):
    name: Optional[str] = None
    ons_code: Optional[str] = None
    median_salary: Optional[float] = None
    median_rent: Optional[float] = None
    year: Optional[int] = None

class RegionResponse(RegionBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)
