from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.embeddings import embed_text
from app.schemas.listing import ListingResponse

router = APIRouter(prefix="/search", tags=["Intelligence"])


class SearchResponse(BaseModel):
    query: str
    results: List[ListingResponse]
    count: int


@router.get(
    "",
    response_model=SearchResponse,
    summary="Semantic search over property listings",
)
def search_listings(
    q: str = Query(..., min_length=3, description="Natural language search query, e.g. 'affordable flat in London'"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    region: Optional[str] = Query(None, description="Optional region filter"),
    db: Session = Depends(get_db),
):
    # Embed the query into the same vector space as listings
    query_vec = embed_text(q)

    # Check that any listings have embeddings at all
    has_embeddings = db.execute(
        text("SELECT 1 FROM listings WHERE embedding IS NOT NULL LIMIT 1")
    ).first()

    if not has_embeddings:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No embeddings found. Run the embedding generation step after importing Land Registry data.",
        )

    # Build the vector similarity query using pgvector cosine distance
    region_filter = "AND LOWER(region) = LOWER(:region)" if region else ""

    sql = text(f"""
        SELECT *
        FROM listings
        WHERE embedding IS NOT NULL
        {region_filter}
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :limit
    """)

    params = {
        "vec": str(query_vec),
        "limit": limit,
    }
    if region:
        params["region"] = region

    rows = db.execute(sql, params).fetchall()

    from app.models.listing import Listing
    results = []
    for row in rows:
        listing = db.query(Listing).filter(Listing.id == row.id).first()
        if listing:
            results.append(listing)

    return SearchResponse(query=q, results=results, count=len(results))
