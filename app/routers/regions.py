from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.region import Region
from app.schemas.region import RegionCreate, RegionUpdate, RegionResponse

import uuid

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("", response_model=List[RegionResponse], summary="List all regions")
def get_regions(db: Session = Depends(get_db)):
    # Returns all UK regions stored in the database
    return db.query(Region).all()


@router.get("/{region_id}", response_model=RegionResponse, summary="Get a single region by ID")
def get_region(region_id: str, db: Session = Depends(get_db)):
    # Returns one region by UUID
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with id '{region_id}' not found",
        )
    return region


@router.post("", response_model=RegionResponse, status_code=status.HTTP_201_CREATED, summary="Create a new region")
def create_region(
    region_in: RegionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # Creates a new region record. Requires JWT authentication.
    existing = db.query(Region).filter(Region.name == region_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Region with name '{region_in.name}' already exists",
        )
    region = Region(
        id=str(uuid.uuid4()),
        **region_in.model_dump(),
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.put("/{region_id}", response_model=RegionResponse, summary="Update a region")
def update_region(
    region_id: str,
    region_in: RegionUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # Updates an existing region. Requires JWT authentication.
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with id '{region_id}' not found",
        )
    update_data = region_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(region, field, value)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a region")
def delete_region(
    region_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    # Permanently deletes a region. Requires JWT authentication. Returns 204.
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with id '{region_id}' not found",
        )
    db.delete(region)
    db.commit()
