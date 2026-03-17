"""
API Router for calculating rent vs. buy comparisons.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.listing import Listing
from app.models.region import Region

router = APIRouter(prefix="/rent-to-buy", tags=["Analytics"])


class RentToBuyResponse(BaseModel):
    """Schema for returning rent vs buy comparison metrics."""
    region: str = Field(..., description="Name of the region", examples=["London"])
    median_house_price: float = Field(..., description="Median house price in the region", examples=[500000.0])
    monthly_mortgage_estimate: float = Field(..., description="Estimated monthly mortgage payment", examples=[2000.0])
    monthly_rent: float = Field(..., description="Median monthly rent in the region", examples=[1800.0])
    monthly_saving_vs_renting: float = Field(..., description="Monthly savings of buying vs renting", examples=[-200.0])
    deposit_10pct: float = Field(..., description="Calculated deposit amount", examples=[50000.0])
    months_to_save_deposit: float = Field(..., description="Estimated months to save the deposit", examples=[60.0])
    years_to_save_deposit: float = Field(..., description="Estimated years to save the deposit", examples=[5.0])
    verdict: str = Field(..., description="Textual verdict of the analysis", examples=["Mortgage costs less than rent."])
    deposit_pct: float = Field(..., description="Deposit percentage used in calculation", examples=[0.10])
    interest_rate: float = Field(..., description="Annual interest rate used in calculation", examples=[4.5])
    term_years: int = Field(..., description="Mortgage term in years used in calculation", examples=[25])

    model_config = {"from_attributes": True}


def _mortgage_monthly(price: float, deposit_pct: float = 0.10, rate_pct: float = 4.5, term_years: int = 25) -> float:
    """
    Standard annuity mortgage formula.
    Default assumptions: 10% deposit, 4.5% annual interest, 25-year term.
    """
    principal = price * (1 - deposit_pct)
    monthly_rate = rate_pct / 100 / 12
    n = term_years * 12
    if monthly_rate == 0:
        return principal / n
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    return round(payment, 2)


@router.get(
    "/{region_name}",
    response_model=RentToBuyResponse,
    summary="Rent-vs-buy comparison for a region",
    responses={
        200: {"description": "Successfully calculated rent vs buy metrics"},
        404: {"description": "Region not found or no listing data available"}
    }
)
def get_rent_to_buy(
    region_name: str,
    deposit_pct: float = Query(0.10, ge=0.05, le=0.40, description="Deposit as a decimal, e.g. 0.10 for 10%"),
    interest_rate: float = Query(4.5, ge=0.1, le=15.0, description="Annual interest rate %"),
    term_years: int = Query(25, ge=5, le=35, description="Mortgage term in years"),
    db: Session = Depends(get_db),
):
    """
    Compares estimated monthly mortgage cost against median rent, and estimates
    how many months a median-salary earner would need to save a deposit.
    
    Mortgage assumptions can be customized via query parameters, but default to:
    - 10% deposit
    - 4.5% p.a. interest (approx. Bank of England base rate + typical lender margin)
    - 25-year repayment term
    
    - **region_name**: Name of the region to analyze (e.g., "London").
    - **deposit_pct**: Deposit percentage as a decimal (default 0.10).
    - **interest_rate**: Annual interest rate percentage (default 4.5).
    - **term_years**: Mortgage term length in years (default 25).
    - **db**: Database session dependency.
    
    Returns a detailed financial comparison and a qualitative verdict on affordability.
    """
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
            detail=f"No listing data found for '{region_name}'. Run the Land Registry importer first.",
        )

    median_price = float(median_price_result)
    rent = float(region.median_rent)
    salary = float(region.median_salary)

    mortgage = _mortgage_monthly(median_price, deposit_pct=deposit_pct, rate_pct=interest_rate, term_years=term_years)
    deposit = median_price * deposit_pct

    # Assume saving 20% of monthly take-home (approx salary * 0.67 * 0.20)
    monthly_take_home = salary / 12 * 0.67
    monthly_saving = monthly_take_home * 0.20
    months_to_save = round(deposit / monthly_saving, 1) if monthly_saving > 0 else 0
    years_to_save = round(months_to_save / 12, 1)

    monthly_saving_vs_renting = round(rent - mortgage, 2)

    # Verdict
    if mortgage < rent and years_to_save < 10:
        verdict = "Buying is cheaper than renting and a deposit is within reach — consider buying."
    elif mortgage < rent:
        verdict = "Mortgage costs less than rent, but saving a deposit takes a long time."
    elif years_to_save < 5:
        verdict = "Renting is cheaper monthly, but a deposit is achievable relatively quickly."
    else:
        verdict = "High prices make both renting and buying challenging in this region."

    return RentToBuyResponse(
        region=region.name,
        median_house_price=round(median_price, 0),
        monthly_mortgage_estimate=mortgage,
        monthly_rent=rent,
        monthly_saving_vs_renting=monthly_saving_vs_renting,
        deposit_10pct=round(deposit, 0),
        months_to_save_deposit=months_to_save,
        years_to_save_deposit=years_to_save,
        verdict=verdict,
        deposit_pct=deposit_pct,
        interest_rate=interest_rate,
        term_years=term_years,
    )
