"""Activity router - manage activities for locations."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.deps import get_db, get_current_user
from app.models import User, Activity, Location

router = APIRouter()


# Pydantic Schemas
class ActivityCreate(BaseModel):
    """Schema for creating an activity."""
    location_id: UUID
    type: Optional[str] = Field(None, max_length=100)
    date: Optional[date] = None


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    type: Optional[str] = Field(None, max_length=100)
    date: Optional[date] = None


class ActivityResponse(BaseModel):
    """Schema for activity response."""
    id: UUID
    location_id: UUID
    type: Optional[str]
    date: Optional[date]

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


@router.get("/location/{location_id}", response_model=List[ActivityResponse])
async def list_activities(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all activities for a location."""
    # Verify location ownership
    await get_location_or_404(db, location_id, current_user.id)
    
    # Fetch activities
    result = await db.execute(
        select(Activity)
        .where(Activity.location_id == location_id)
        .order_by(Activity.date.desc())
    )
    activities = result.scalars().all()
    
    return activities


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new activity."""
    # Verify location ownership
    await get_location_or_404(db, data.location_id, current_user.id)
    
    # Create activity
    activity = Activity(
        location_id=data.location_id,
        type=data.type,
        date=data.date
    )
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an activity."""
    # Get activity
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, activity.location_id, current_user.id)
    
    # Update fields
    if data.type is not None:
        activity.type = data.type
    if data.date is not None:
        activity.date = data.date
    
    await db.commit()
    await db.refresh(activity)
    
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an activity."""
    # Get activity
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, activity.location_id, current_user.id)
    
    # Delete
    await db.delete(activity)
    await db.commit()
    
    return None
