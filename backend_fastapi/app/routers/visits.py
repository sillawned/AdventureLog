"""Visit endpoints using SQLAlchemy ORM."""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from datetime import date
from typing import Optional, List
from pydantic import BaseModel

from app.models.base import get_db
from app.models.user import User
from app.crud.adventure import (
    get_visit_by_id,
    get_visits_by_user,
    count_visits_by_user,
    create_visit as crud_create_visit,
    update_visit as crud_update_visit,
    delete_visit as crud_delete_visit,
    get_location_by_id,
)
from app.deps import get_current_user

router = APIRouter()


# Schemas
class VisitCreate(BaseModel):
    location_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


class VisitUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


class LocationSummary(BaseModel):
    """Nested location data for visit response."""
    id: str
    name: str
    city: Optional[str]
    country: Optional[str]
    
    class Config:
        from_attributes = True


class VisitOut(BaseModel):
    id: str
    location_id: str
    location: Optional[LocationSummary] = None
    start_date: Optional[date]
    end_date: Optional[date]
    timezone: Optional[str]
    notes: Optional[str]

    @classmethod
    def from_orm_visit(cls, visit, include_location: bool = False):
        location_data = None
        if include_location and visit.location:
            location_data = LocationSummary(
                id=str(visit.location.id),
                name=visit.location.name,
                city=visit.location.city,
                country=visit.location.country
            )
        
        return cls(
            id=str(visit.id),
            location_id=str(visit.location_id),
            location=location_data,
            start_date=visit.start_date,
            end_date=visit.end_date,
            timezone=visit.timezone,
            notes=visit.notes
        )


class VisitListResponse(BaseModel):
    """Schema for paginated visit list."""
    total: int
    visits: List[VisitOut]


@router.get('/', response_model=VisitListResponse)
async def list_visits(
    limit: int = Query(default=100, le=100),
    offset: int = Query(default=0, ge=0),
    location_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all visits for the current user."""
    # Optional filter by location, ensuring ownership
    if location_id:
        location = await get_location_by_id(db, location_id)
        if not location or location.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        # Simple filtered query without adding new CRUD: reuse get_visits_by_user then filter
        visits = [v for v in await get_visits_by_user(db=db, user_id=current_user.id, limit=limit, offset=offset) if v.location_id == location_id]
        total = len(visits)
    else:
        visits = await get_visits_by_user(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        total = await count_visits_by_user(db=db, user_id=current_user.id)
    
    return VisitListResponse(
        total=total,
        visits=[VisitOut.from_orm_visit(visit, include_location=True) for visit in visits]
    )


@router.post('/', response_model=VisitOut, status_code=status.HTTP_201_CREATED)
async def create_visit(
    payload: VisitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new visit for a location."""
    # Verify location exists and user has access
    location = await get_location_by_id(db, payload.location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    if location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add visits to this location"
        )
    
    # Create the visit
    new_id = uuid4()
    visit = await crud_create_visit(
        db=db,
        visit_id=new_id,
        location_id=payload.location_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        timezone=payload.timezone,
        notes=payload.notes,
    )
    
    await db.commit()
    return VisitOut.from_orm_visit(visit)


@router.get('/{visit_id}', response_model=VisitOut)
async def get_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a visit by ID."""
    from uuid import UUID
    
    try:
        visit_uuid = UUID(visit_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visit ID format"
        )
    
    visit = await get_visit_by_id(db, visit_uuid)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    
    # Check ownership through location
    location = await get_location_by_id(db, visit.location_id)
    if not location or location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this visit"
        )
    
    return VisitOut.from_orm_visit(visit)


@router.patch('/{visit_id}', response_model=VisitOut)
async def update_visit(
    visit_id: str,
    payload: VisitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a visit."""
    from uuid import UUID
    
    try:
        visit_uuid = UUID(visit_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visit ID format"
        )
    
    visit = await get_visit_by_id(db, visit_uuid)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    
    # Check ownership through location
    location = await get_location_by_id(db, visit.location_id)
    if not location or location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this visit"
        )
    
    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return VisitOut.from_orm_visit(visit)
    
    updated_visit = await crud_update_visit(db, visit, **update_data)
    await db.commit()
    
    return VisitOut.from_orm_visit(updated_visit)


@router.delete('/{visit_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a visit."""
    from uuid import UUID
    
    try:
        visit_uuid = UUID(visit_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid visit ID format"
        )
    
    visit = await get_visit_by_id(db, visit_uuid)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    
    # Check ownership through location
    location = await get_location_by_id(db, visit.location_id)
    if not location or location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this visit"
        )
    
    await crud_delete_visit(db, visit)
    await db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

