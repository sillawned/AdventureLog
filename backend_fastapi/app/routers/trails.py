"""Trail router - manage hiking trails for locations."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.deps import get_db, get_current_user
from app.models import User, Trail, Location

router = APIRouter()


# Pydantic Schemas
class TrailCreate(BaseModel):
    """Schema for creating a trail."""
    location_id: UUID
    name: str = Field(..., max_length=255)
    difficulty: Optional[str] = Field(None, max_length=50)
    length: Optional[float] = None


class TrailUpdate(BaseModel):
    """Schema for updating a trail."""
    name: Optional[str] = Field(None, max_length=255)
    difficulty: Optional[str] = Field(None, max_length=50)
    length: Optional[float] = None


class TrailResponse(BaseModel):
    """Schema for trail response."""
    id: UUID
    location_id: UUID
    name: str
    difficulty: Optional[str]
    length: Optional[float]

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


@router.get("/location/{location_id}", response_model=List[TrailResponse])
async def list_trails(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all trails for a location."""
    # Verify location ownership
    await get_location_or_404(db, location_id, current_user.id)
    
    # Fetch trails
    result = await db.execute(
        select(Trail)
        .where(Trail.location_id == location_id)
    )
    trails = result.scalars().all()
    
    return trails


@router.post("/", response_model=TrailResponse, status_code=status.HTTP_201_CREATED)
async def create_trail(
    data: TrailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new trail."""
    # Verify location ownership
    await get_location_or_404(db, data.location_id, current_user.id)
    
    # Create trail
    trail = Trail(
        location_id=data.location_id,
        name=data.name,
        difficulty=data.difficulty,
        length=data.length
    )
    
    db.add(trail)
    await db.commit()
    await db.refresh(trail)
    
    return trail


@router.put("/{trail_id}", response_model=TrailResponse)
async def update_trail(
    trail_id: UUID,
    data: TrailUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a trail."""
    # Get trail
    result = await db.execute(
        select(Trail).where(Trail.id == trail_id)
    )
    trail = result.scalar_one_or_none()
    
    if not trail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trail not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, trail.location_id, current_user.id)
    
    # Update fields
    if data.name is not None:
        trail.name = data.name
    if data.difficulty is not None:
        trail.difficulty = data.difficulty
    if data.length is not None:
        trail.length = data.length
    
    await db.commit()
    await db.refresh(trail)
    
    return trail


@router.delete("/{trail_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trail(
    trail_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a trail."""
    # Get trail
    result = await db.execute(
        select(Trail).where(Trail.id == trail_id)
    )
    trail = result.scalar_one_or_none()
    
    if not trail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trail not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, trail.location_id, current_user.id)
    
    # Delete
    await db.delete(trail)
    await db.commit()
    
    return None
