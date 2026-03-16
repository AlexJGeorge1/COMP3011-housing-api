from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.database import get_db
from app.models.listing import Listing
from app.models.region import Region

router = APIRouter(prefix="/rent-to-buy", tags=["Analytics"])


class RentToBuyResponse(BaseModel):
    region: str
    median_house_price: float
    monthly_mortgage_estimate: float
    monthly_rent: float
    monthly_saving_vs_renting: float
    deposit_10pct: float
    months_to_save_deposit: float
    years_to_save_deposit: float
    verdict: str

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
)
def get_rent_to_buy(region_name: str, db: Session = Depends(get_db)):
    """
    Compares estimated monthly mortgage cost against median rent, and estimates
    how many months a median-salary earner would need to save a 10% deposit.

    Mortgage assumptions: 10% deposit, 4.5% p.a. interest (approx. Bank of England
    base rate + typical lender margin), 25-year repayment term.
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

    mortgage = _mortgage_monthly(median_price)
    deposit = median_price * 0.10

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
    )
