from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.listing import Listing
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

import uuid

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get("", response_model=List[ListingResponse], summary="List all property listings")
def get_listings(
    region: Optional[str] = Query(None, description="Filter by region name"),
    limit: int = Query(100, le=500, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip (for pagination)"),
    db: Session = Depends(get_db),
):
    query = db.query(Listing)
    if region:
        query = query.filter(Listing.region.ilike(f"%{region}%"))
    return query.offset(offset).limit(limit).all()


@router.get("/{listing_id}", response_model=ListingResponse, summary="Get a single listing by ID")
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    """Returns one property listing"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing with id '{listing_id}' not found",
        )
    return listing


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED, summary="Create a new listing")
def create_listing(
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):

    """Creates a new property listing. Requires JWT authentication."""

    listing = Listing(
        id=str(uuid.uuid4()),
        **listing_in.model_dump(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.put("/{listing_id}", response_model=ListingResponse, summary="Update a listing")
def update_listing(
    listing_id: str,
    listing_in: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Updates the fields of an existing listing."""
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


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a listing")
def delete_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """Deletes a property listing."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Listing with id '{listing_id}' not found",
        )
    db.delete(listing)
    db.commit()
