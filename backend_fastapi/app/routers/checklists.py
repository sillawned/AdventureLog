"""Checklist router - manage checklists and checklist items."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.deps import get_db, get_current_user
from app.models import User, Checklist, ChecklistItem, Location

router = APIRouter()


# Pydantic Schemas
class ChecklistItemCreate(BaseModel):
    """Schema for creating a checklist item."""
    name: str = Field(..., max_length=255)
    is_checked: bool = False


class ChecklistItemUpdate(BaseModel):
    """Schema for updating a checklist item."""
    name: Optional[str] = Field(None, max_length=255)
    is_checked: Optional[bool] = None


class ChecklistItemResponse(BaseModel):
    """Schema for checklist item response."""
    id: UUID
    checklist_id: UUID
    name: str
    is_checked: bool

    class Config:
        from_attributes = True


class ChecklistCreate(BaseModel):
    """Schema for creating a checklist."""
    location_id: UUID
    name: str = Field(..., max_length=255)
    items: List[ChecklistItemCreate] = []


class ChecklistUpdate(BaseModel):
    """Schema for updating a checklist."""
    name: Optional[str] = Field(None, max_length=255)


class ChecklistResponse(BaseModel):
    """Schema for checklist response."""
    id: UUID
    location_id: UUID
    name: str
    items: List[ChecklistItemResponse] = []

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


@router.get("/location/{location_id}", response_model=List[ChecklistResponse])
async def list_checklists(
    location_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all checklists for a location with their items."""
    # Verify location ownership
    await get_location_or_404(db, location_id, current_user.id)
    
    # Fetch checklists with items
    result = await db.execute(
        select(Checklist)
        .where(Checklist.location_id == location_id)
        .options(selectinload(Checklist.items))
    )
    checklists = result.scalars().all()
    
    return checklists


@router.post("/", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    data: ChecklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new checklist with optional items."""
    # Verify location ownership
    await get_location_or_404(db, data.location_id, current_user.id)
    
    # Create checklist
    checklist = Checklist(
        location_id=data.location_id,
        name=data.name
    )
    
    db.add(checklist)
    await db.flush()  # Get checklist ID
    
    # Create items if provided
    for item_data in data.items:
        item = ChecklistItem(
            checklist_id=checklist.id,
            name=item_data.name,
            is_checked=item_data.is_checked
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(checklist)
    
    # Load items
    result = await db.execute(
        select(Checklist)
        .where(Checklist.id == checklist.id)
        .options(selectinload(Checklist.items))
    )
    checklist = result.scalar_one()
    
    return checklist


@router.put("/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: UUID,
    data: ChecklistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a checklist (name only, use item endpoints for items)."""
    # Get checklist
    result = await db.execute(
        select(Checklist)
        .where(Checklist.id == checklist_id)
        .options(selectinload(Checklist.items))
    )
    checklist = result.scalar_one_or_none()
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, checklist.location_id, current_user.id)
    
    # Update fields
    if data.name is not None:
        checklist.name = data.name
    
    await db.commit()
    await db.refresh(checklist)
    
    return checklist


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a checklist (and all its items via cascade)."""
    # Get checklist
    result = await db.execute(
        select(Checklist).where(Checklist.id == checklist_id)
    )
    checklist = result.scalar_one_or_none()
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, checklist.location_id, current_user.id)
    
    # Delete (items cascade automatically)
    await db.delete(checklist)
    await db.commit()
    
    return None


# Checklist Item endpoints
@router.post("/{checklist_id}/items", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_checklist_item(
    checklist_id: UUID,
    data: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to a checklist."""
    # Get checklist
    result = await db.execute(
        select(Checklist).where(Checklist.id == checklist_id)
    )
    checklist = result.scalar_one_or_none()
    
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found"
        )
    
    # Verify location ownership
    await get_location_or_404(db, checklist.location_id, current_user.id)
    
    # Create item
    item = ChecklistItem(
        checklist_id=checklist_id,
        name=data.name,
        is_checked=data.is_checked
    )
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    return item


@router.put("/items/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    item_id: UUID,
    data: ChecklistItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a checklist item."""
    # Get item with checklist
    result = await db.execute(
        select(ChecklistItem)
        .where(ChecklistItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found"
        )
    
    # Get checklist to verify ownership
    result = await db.execute(
        select(Checklist).where(Checklist.id == item.checklist_id)
    )
    checklist = result.scalar_one()
    
    # Verify location ownership
    await get_location_or_404(db, checklist.location_id, current_user.id)
    
    # Update fields
    if data.name is not None:
        item.name = data.name
    if data.is_checked is not None:
        item.is_checked = data.is_checked
    
    await db.commit()
    await db.refresh(item)
    
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a checklist item."""
    # Get item
    result = await db.execute(
        select(ChecklistItem).where(ChecklistItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist item not found"
        )
    
    # Get checklist to verify ownership
    result = await db.execute(
        select(Checklist).where(Checklist.id == item.checklist_id)
    )
    checklist = result.scalar_one()
    
    # Verify location ownership
    await get_location_or_404(db, checklist.location_id, current_user.id)
    
    # Delete
    await db.delete(item)
    await db.commit()
    
    return None
