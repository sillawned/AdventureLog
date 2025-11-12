"""Transportation router - manage transportation methods for locations."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from datetime import datetime

from app.deps import get_db, get_current_user
from app.models import User, Transportation, Location

router = APIRouter()


# Pydantic Schemas
class TransportationCreate(BaseModel):
    """Schema for creating a transportation with extended fields."""
    location_id: UUID
    type: Optional[str] = Field(None, max_length=100)
    from_location: Optional[str] = Field(None, max_length=255)
    to_location: Optional[str] = Field(None, max_length=255)
    depart_time: Optional[datetime] = None
    arrive_time: Optional[datetime] = None
    depart_timezone: Optional[str] = Field(None, max_length=50)
    arrive_timezone: Optional[str] = Field(None, max_length=50)
    depart_latitude: Optional[float] = None
    depart_longitude: Optional[float] = None
    arrive_latitude: Optional[float] = None
    arrive_longitude: Optional[float] = None
    link: Optional[str] = Field(None, max_length=500)
    rating: Optional[int] = None
    is_public: bool = False
    collection_id: Optional[UUID] = None


class TransportationUpdate(BaseModel):
    """Schema for updating a transportation."""
    type: Optional[str] = Field(None, max_length=100)
    from_location: Optional[str] = Field(None, max_length=255)
    to_location: Optional[str] = Field(None, max_length=255)
    depart_time: Optional[datetime] = None
    arrive_time: Optional[datetime] = None
    depart_timezone: Optional[str] = Field(None, max_length=50)
    arrive_timezone: Optional[str] = Field(None, max_length=50)
    depart_latitude: Optional[float] = None
    depart_longitude: Optional[float] = None
    arrive_latitude: Optional[float] = None
    arrive_longitude: Optional[float] = None
    link: Optional[str] = Field(None, max_length=500)
    rating: Optional[int] = None
    is_public: Optional[bool] = None
    collection_id: Optional[UUID] = None


class TransportationResponse(BaseModel):
    """Schema for transportation response."""
    id: UUID
    location_id: UUID
    type: Optional[str]
    from_location: Optional[str]
    to_location: Optional[str]
    depart_time: Optional[datetime]
    arrive_time: Optional[datetime]
    depart_timezone: Optional[str]
    arrive_timezone: Optional[str]
    depart_latitude: Optional[float]
    depart_longitude: Optional[float]
    arrive_latitude: Optional[float]
    arrive_longitude: Optional[float]
    link: Optional[str]
    rating: Optional[int]
    is_public: bool
    collection_id: Optional[UUID]

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


@router.get("/location/{location_id}", response_model=List[TransportationResponse])
async def list_transportations(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all transportations for a location."""
    # Verify location ownership
    await get_location_or_404(db, location_id, current_user.id)
    
    # Fetch transportations
    result = await db.execute(
        select(Transportation)
        .where(Transportation.location_id == location_id)
    )
    transportations = result.scalars().all()
    
    return transportations


@router.post("/", response_model=TransportationResponse, status_code=status.HTTP_201_CREATED)
async def create_transportation(
    data: TransportationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transportation."""
    # Verify location ownership
    await get_location_or_404(db, data.location_id, current_user.id)
    
    # Create transportation
    transportation = Transportation(
        id=uuid4(),
        location_id=data.location_id,
        type=data.type,
        from_location=data.from_location,
        to_location=data.to_location,
        depart_time=data.depart_time,
        arrive_time=data.arrive_time,
        depart_timezone=data.depart_timezone,
        arrive_timezone=data.arrive_timezone,
        depart_latitude=data.depart_latitude,
        depart_longitude=data.depart_longitude,
        arrive_latitude=data.arrive_latitude,
        arrive_longitude=data.arrive_longitude,
        link=data.link,
        rating=data.rating,
        is_public=data.is_public,
        collection_id=data.collection_id,
    )
    
    db.add(transportation)
    await db.commit()
    await db.refresh(transportation)
    
    return transportation


@router.put("/{transportation_id}", response_model=TransportationResponse)
async def update_transportation(
    transportation_id: UUID,
    data: TransportationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transportation."""
    # Get transportation
    result = await db.execute(
        select(Transportation).where(Transportation.id == transportation_id)
    )
    transportation = result.scalar_one_or_none()
    
    if not transportation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transportation not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, transportation.location_id, current_user.id)
    
    # Update fields
    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(transportation, key, value)
    
    await db.commit()
    await db.refresh(transportation)
    
    return transportation


@router.delete("/{transportation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transportation(
    transportation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transportation."""
    # Get transportation
    result = await db.execute(
        select(Transportation).where(Transportation.id == transportation_id)
    )
    transportation = result.scalar_one_or_none()
    
    if not transportation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transportation not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, transportation.location_id, current_user.id)
    
    # Delete
    await db.delete(transportation)
    await db.commit()
    
    return None
