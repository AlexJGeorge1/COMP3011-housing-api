from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.config import get_settings

from app.database import get_db
from app.models.listing import Listing
from app.models.region import Region

router = APIRouter(prefix="/insights", tags=["Intelligence"])


class InsightsResponse(BaseModel):
    region: str
    insight: str
    data_used: dict
    powered_by: str


def _call_llm(prompt: str) -> tuple[str, str]:
# call groq api 
    settings = get_settings()
    api_key = settings.groq_api_key
    if not api_key or api_key == "your-groq-api-key-here":
        return (
            "AI insights are unavailable (no GROQ_API_KEY configured). "
            "Get a free key at https://console.groq.com and add it to your .env file.",
            "fallback",
        )

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip(), "llama-3.1-8b-instant (Groq)"
    except Exception as e:
        return f"AI insight generation failed: {str(e)}", "error"


@router.get(
    "/{region_name}",
    response_model=InsightsResponse,
    summary="AI-generated housing market intelligence for a region",
)
def get_insights(region_name: str, db: Session = Depends(get_db)):
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

    # Gather live statistics to ground the AI in real data
    median_price = (
        db.query(func.percentile_cont(0.5).within_group(Listing.price.asc()))
        .filter(func.lower(Listing.region) == region.name.lower())
        .scalar()
    )

    listing_count = (
        db.query(func.count(Listing.id))
        .filter(func.lower(Listing.region) == region.name.lower())
        .scalar()
    )

    latest_year = (
        db.query(func.max(func.extract("year", Listing.transaction_date)))
        .filter(func.lower(Listing.region) == region.name.lower())
        .scalar()
    )

    data_used = {
        "median_house_price": round(float(median_price), 0) if median_price else None,
        "median_salary": float(region.median_salary) if region.median_salary else None,
        "median_rent_monthly": float(region.median_rent) if region.median_rent else None,
        "price_to_income_ratio": (
            round(float(median_price) / float(region.median_salary), 2)
            if median_price and region.median_salary else None
        ),
        "transaction_count": listing_count,
        "data_year": int(latest_year) if latest_year else region.year,
    }

    if median_price is None:
        return InsightsResponse(
            region=region.name,
            insight=(
                f"No transaction data is available for {region.name} yet. "
                "Run the Land Registry importer first, then try again."
            ),
            data_used=data_used,
            powered_by="fallback",
        )

    prompt = f"""You are a UK housing market analyst. Based ONLY on the data below, write a concise 3–4 sentence 
insight about housing affordability in {region.name}. Be specific with the numbers. Do not use bullet points.
Do not invent data not listed below.

Data for {region.name} ({data_used['data_year']}):
- Median house price: £{data_used['median_house_price']:,.0f}
- Median gross annual salary: £{data_used['median_salary']:,.0f}
- Median monthly private rent: £{data_used['median_rent_monthly']:,.0f}
- Price-to-income ratio: {data_used['price_to_income_ratio']}x
- Transactions in dataset: {data_used['transaction_count']:,}

Write 3–4 sentences aimed at a first-time buyer or renter."""

    insight_text, model_name = _call_llm(prompt)

    return InsightsResponse(
        region=region.name,
        insight=insight_text,
        data_used=data_used,
        powered_by=model_name,
    )
