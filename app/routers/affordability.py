from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.listing import Listing
from app.models.region import Region

router = APIRouter(prefix="/affordability", tags=["Analytics"])


class AffordabilityResponse(BaseModel):
    region: str
    ons_code: str
    year: int
    median_salary: float
    median_rent_monthly: float
    median_house_price: float
    price_to_income_ratio: float
    rent_to_income_pct: float
    affordability_band: str

    model_config = {"from_attributes": True}


def _affordability_band(ratio: float) -> str:
    """Classify affordability based on price-to-income ratio."""
    if ratio < 4:
        return "affordable"
    elif ratio < 7:
        return "moderately unaffordable"
    elif ratio < 10:
        return "seriously unaffordable"
    else:
        return "severely unaffordable"


@router.get(
    "/{region_name}",
    response_model=AffordabilityResponse,
    summary="Housing affordability metrics for a region",
)
def get_affordability(region_name: str, db: Session = Depends(get_db)):
    # Look up the region 

    region = (
        db.query(Region)
        .filter(func.lower(Region.name) == region_name.strip().lower())
        .first()
    )
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region '{region_name}' not found. Check GET /regions for valid names.",
        )
    median_price_result = (
        db.query(func.percentile_cont(0.5).within_group(Listing.price.asc()))
        .filter(func.lower(Listing.region) == region.name.lower())
        .scalar()
    )

    if median_price_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No listing data found for region '{region_name}'. Run the Land Registry importer first.",
        )

    median_price = float(median_price_result)
    salary = float(region.median_salary)
    rent = float(region.median_rent)

    price_to_income = round(median_price / salary, 2)
    rent_to_income_pct = round((rent * 12) / salary * 100, 1)

    return AffordabilityResponse(
        region=region.name,
        ons_code=region.ons_code,
        year=region.year,
        median_salary=salary,
        median_rent_monthly=rent,
        median_house_price=median_price,
        price_to_income_ratio=price_to_income,
        rent_to_income_pct=rent_to_income_pct,
        affordability_band=_affordability_band(price_to_income),
    )
