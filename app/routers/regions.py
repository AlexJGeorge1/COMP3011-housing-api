"""
API Router for managing ONS regions.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.region import Region
from app.schemas.region import RegionCreate, RegionUpdate, RegionResponse

import uuid

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get(
    "",
    response_model=List[RegionResponse],
    summary="List all regions",
    responses={200: {"description": "Successfully retrieved list of regions"}}
)
def get_regions(db: Session = Depends(get_db)):
    """
    Retrieve all UK regions stored in the database.
    
    Returns a list of regions, including their names, ONS codes, and aggregated economic data 
    (median salary and median rent) if available.
    """
    return db.query(Region).all()


@router.get(
    "/{region_id}",
    response_model=RegionResponse,
    summary="Get a single region by ID",
    responses={
        200: {"description": "Successfully retrieved the region"},
        404: {"description": "Region not found"}
    }
)
def get_region(region_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single region by its unique UUID.
    
    - **region_id**: The UUID of the region to retrieve.
    """
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with id '{region_id}' not found",
        )
    return region


@router.post(
    "",
    response_model=RegionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new region",
    responses={
        201: {"description": "Region successfully created"},
        401: {"description": "Unauthorized - Valid JWT token required"},
        409: {"description": "Conflict - Region with this name already exists"}
    }
)
def create_region(
    region_in: RegionCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Create a new region record.
    
    Requires JWT authentication.
    
    - **region_in**: The region data to create.
    """
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


@router.put(
    "/{region_id}",
    response_model=RegionResponse,
    summary="Update a region",
    responses={
        200: {"description": "Region successfully updated"},
        401: {"description": "Unauthorized - Valid JWT token required"},
        404: {"description": "Region not found"}
    }
)
def update_region(
    region_id: str,
    region_in: RegionUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Update an existing region record.
    
    Requires JWT authentication. Only the fields provided in the request will be updated.
    
    - **region_id**: The UUID of the region to update.
    - **region_in**: The updated region data.
    """
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


@router.delete(
    "/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a region",
    responses={
        204: {"description": "Region successfully deleted"},
        401: {"description": "Unauthorized - Valid JWT token required"},
        404: {"description": "Region not found"}
    }
)
def delete_region(
    region_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Permanently delete a region.
    
    Requires JWT authentication.
    
    - **region_id**: The UUID of the region to delete.
    """
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with id '{region_id}' not found",
        )
    db.delete(region)
    db.commit()
