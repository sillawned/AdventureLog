"""Lodging router - manage lodging accommodations for locations."""
from __future__ import annotations

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.deps import get_db, get_current_user
from app.models import User, Lodging, Location

router = APIRouter()


# Pydantic Schemas
class LodgingCreate(BaseModel):
    """Schema for creating lodging."""
    location_id: UUID
    name: str = Field(..., max_length=255)


class LodgingUpdate(BaseModel):
    """Schema for updating lodging."""
    name: str = Field(..., max_length=255)


class LodgingResponse(BaseModel):
    """Schema for lodging response."""
    id: UUID
    location_id: UUID
    name: str

    class Config:
        from_attributes = True


# Helper functions
async def get_location_or_404(db: AsyncSession, location_id: UUID, user_id: int) -> Location:
    """Get location and verify ownership."""
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    if location.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this location"
        )
    
    return location


@router.get("/location/{location_id}", response_model=List[LodgingResponse])
async def list_lodgings(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all lodgings for a location."""
    # Verify location ownership
    await get_location_or_404(db, location_id, current_user.id)
    
    # Fetch lodgings
    result = await db.execute(
        select(Lodging)
        .where(Lodging.location_id == location_id)
    )
    lodgings = result.scalars().all()
    
    return lodgings


@router.post("/", response_model=LodgingResponse, status_code=status.HTTP_201_CREATED)
async def create_lodging(
    data: LodgingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lodging."""
    # Verify location ownership
    await get_location_or_404(db, data.location_id, current_user.id)
    
    # Create lodging
    lodging = Lodging(
        location_id=data.location_id,
        name=data.name
    )
    
    db.add(lodging)
    await db.commit()
    await db.refresh(lodging)
    
    return lodging


@router.put("/{lodging_id}", response_model=LodgingResponse)
async def update_lodging(
    lodging_id: UUID,
    data: LodgingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a lodging."""
    # Get lodging
    result = await db.execute(
        select(Lodging).where(Lodging.id == lodging_id)
    )
    lodging = result.scalar_one_or_none()
    
    if not lodging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lodging not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, lodging.location_id, current_user.id)
    
    # Update name
    lodging.name = data.name
    
    await db.commit()
    await db.refresh(lodging)
    
    return lodging


@router.delete("/{lodging_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lodging(
    lodging_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a lodging."""
    # Get lodging
    result = await db.execute(
        select(Lodging).where(Lodging.id == lodging_id)
    )
    lodging = result.scalar_one_or_none()
    
    if not lodging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lodging not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, lodging.location_id, current_user.id)
    
    # Delete
    await db.delete(lodging)
    await db.commit()
    
    return None
