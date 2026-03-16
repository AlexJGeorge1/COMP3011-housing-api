from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.listing import Listing
from app.models.region import Region

router = APIRouter(prefix="/trends", tags=["Analytics"])


class YearlyPoint(BaseModel):
    year: int
    median_price: float
    transaction_count: int


class TrendsResponse(BaseModel):
    region: str
    data_from: int
    data_to: int
    yearly_data: List[YearlyPoint]
    total_change_pct: float
    cagr_pct: float

    model_config = {"from_attributes": True}


@router.get(
    "/{region_name}",
    response_model=TrendsResponse,
    summary="Year-on-year house price trends for a region",
)
def get_trends(region_name: str, db: Session = Depends(get_db)):
    # Validate region exists
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

    rows = (
        db.query(
            extract("year", Listing.transaction_date).label("year"),
            func.percentile_cont(0.5).within_group(Listing.price.asc()).label("median_price"),
            func.count(Listing.id).label("transaction_count"),
        )
        .filter(func.lower(Listing.region) == region.name.lower())
        .group_by("year")
        .order_by("year")
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No listing data found for '{region_name}'. Run the Land Registry importer first.",
        )

    yearly_data = [
        YearlyPoint(
            year=int(row.year),
            median_price=round(float(row.median_price), 0),
            transaction_count=row.transaction_count,
        )
        for row in rows
    ]

    first_price = yearly_data[0].median_price
    last_price = yearly_data[-1].median_price
    n_years = yearly_data[-1].year - yearly_data[0].year

    total_change_pct = round((last_price - first_price) / first_price * 100, 1)
    # CAGR = (end/start)^(1/n) - 1
    cagr_pct = round(((last_price / first_price) ** (1 / n_years) - 1) * 100, 2) if n_years > 0 else 0.0

    return TrendsResponse(
        region=region.name,
        data_from=yearly_data[0].year,
        data_to=yearly_data[-1].year,
        yearly_data=yearly_data,
        total_change_pct=total_change_pct,
        cagr_pct=cagr_pct,
    )
