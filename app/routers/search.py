"""
API Router for semantic search functionality over property listings.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.embeddings import embed_text
from app.schemas.listing import ListingResponse

router = APIRouter(prefix="/search", tags=["Intelligence"])


class SearchResponse(BaseModel):
    """Schema for the semantic search response."""
    query: str = Field(..., description="The original search query", examples=["affordable flat in London"])
    results: List[ListingResponse] = Field(..., description="List of matching property listings")
    count: int = Field(..., description="Number of results returned", examples=[10])


@router.get(
    "",
    response_model=SearchResponse,
    summary="Semantic search over property listings",
    responses={
        200: {"description": "Successful search"},
        422: {"description": "No embeddings found or validation error"},
        503: {"description": "Semantic search unavailable due to missing pgvector extension"}
    }
)
def search_listings(
    q: str = Query(..., min_length=3, description="Natural language search query, e.g. 'affordable flat in London'"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    region: Optional[str] = Query(None, description="Optional region filter"),
    db: Session = Depends(get_db),
):
    """
    Perform a semantic search over property listings.
    
    Expects a natural language query and uses vector embeddings (pgvector) to find 
    the most relevant property listings based on cosine similarity.
    
    - **q**: The natural language search query string.
    - **limit**: Maximum number of listings to return (default 10, max 50).
    - **region**: Optional filter to restrict search to a specific ONS region.
    - **db**: Database session dependency.
    
    Returns a list of listings matching the query semantically, along with the original query and count.
    """
    # Check that the embedding column exists (pgvector may not be available)
    try:
        has_embeddings = db.execute(
            text("SELECT 1 FROM listings WHERE embedding IS NOT NULL LIMIT 1")
        ).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Semantic search is unavailable because the pgvector extension "
                "is not installed on this PostgreSQL instance. "
                "CRUD, analytics, and insights endpoints remain fully functional."
            ),
        )

    # Embed the query into the same vector space as listings
    query_vec = embed_text(q)

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

    from app.models.listing import Listing
    # Fetch results from the DB and map them directly to SQLAlchemy Ranking models
    # This avoids the N+1 query problem by hydrating models in one roundtrip
    results = db.query(Listing).from_statement(sql).params(**params).all()

    return SearchResponse(query=q, results=results, count=len(results))
