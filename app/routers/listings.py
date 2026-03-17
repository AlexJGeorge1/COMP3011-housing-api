import logging
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.listing import Listing
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.embeddings import embed_listing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get(
    "",
    response_model=List[ListingResponse],
    summary="List all property listings",
    description="Retrieve a paginated list of property listings. Optionally filter by region name."
)
def get_listings(
    region: Optional[str] = Query(None, description="Filter by region name (case-insensitive partial match)", examples=["London"]),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results to return", examples=[50]),
    offset: int = Query(0, ge=0, description="Number of results to skip (for pagination)", examples=[0]),
    db: Session = Depends(get_db),
):
    """
    Fetch a list of property listings from the database.
    
    - **region**: Optional string to filter listings where region contains the value.
    - **limit**: Limits the number of returned records (max 500).
    - **offset**: Number of records to skip for pagination.
    """
    query = db.query(Listing)
    if region:
        query = query.filter(Listing.region.ilike(f"%{region}%"))
    return query.offset(offset).limit(limit).all()


@router.get(
    "/{listing_id}",
    response_model=ListingResponse,
    summary="Get a single listing by ID",
    description="Retrieves the details of a specific property listing using its unique identifier.",
    responses={
        404: {"description": "Listing not found"}
    }
)
def get_listing(
    listing_id: Annotated[str, Path(description="The UUID of the listing to retrieve", examples=["123e4567-e89b-12d3-a456-426614174000"])],
    db: Session = Depends(get_db)
):
    """
    Returns one property listing based on the provided UUID.
    
    Raises a 404 HTTP exception if the listing does not exist in the database.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing with id '{listing_id}' not found",
        )
    return listing


@router.post(
    "",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new listing",
    description="Creates a new property transaction listing in the database. Requires JWT authentication.",
    responses={
        201: {"description": "The newly created listing."},
        401: {"description": "Unauthorized - Valid JWT token required."},
    }
)
def create_listing(
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):

    """
    Creates a new property listing.
    
    Requires an authenticated user (JWT). The newly created listing will have a randomly 
    generated UUID. An attempt to generate an embedding for the listing will also be made.
    """

    listing = Listing(
        id=str(uuid.uuid4()),
        **listing_in.model_dump(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    try:
        listing.embedding = embed_listing(listing)
        db.commit()
        db.refresh(listing)
    except Exception:
        logger.warning("Failed to generate embedding for listing %s", listing.id)

    return listing


@router.put(
    "/{listing_id}",
    response_model=ListingResponse,
    summary="Update a listing",
    description="Updates the fields of an existing property listing. Requires JWT authentication.",
    responses={
        200: {"description": "The updated listing."},
        401: {"description": "Unauthorized - Valid JWT token required."},
        404: {"description": "Listing not found."},
    }
)
def update_listing(
    listing_id: Annotated[str, Path(description="The UUID of the listing to update", examples=["123e4567-e89b-12d3-a456-426614174000"])],
    listing_in: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Updates the specified fields of an existing property listing.
    
    Only the fields provided in the request body will be updated. Requires an authenticated user.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing with id '{listing_id}' not found",
        )
    update_data = listing_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete(
    "/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a listing",
    description="Deletes a property listing from the database. Requires JWT authentication.",
    responses={
        204: {"description": "Listing successfully deleted."},
        401: {"description": "Unauthorized - Valid JWT token required."},
        404: {"description": "Listing not found."},
    }
)
def delete_listing(
    listing_id: Annotated[str, Path(description="The UUID of the listing to delete", examples=["123e4567-e89b-12d3-a456-426614174000"])],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Deletes a property listing based on the provided UUID.
    
    Requires an authenticated user.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing with id '{listing_id}' not found",
        )
    db.delete(listing)
    db.commit()
