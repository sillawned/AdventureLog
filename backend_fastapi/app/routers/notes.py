"""Notes CRUD router."""

import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.adventure import Note
from app.models.user import User
from app.deps import get_current_user
from app.crud.adventure import get_notes_by_location, create_note, get_location_by_id

router = APIRouter()


# --- Schemas ---

class NoteCreate(BaseModel):
    """Schema for creating a note."""
    location_id: str
    name: str
    content: str


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: str
    location_id: str
    name: str
    content: str
    created_at: datetime

    @classmethod
    def from_orm_note(cls, note: Note) -> "NoteResponse":
        """Create response from ORM Note object."""
        return cls(
            id=str(note.id),
            location_id=str(note.location_id),
            name=note.name,
            content=note.content or "",
            created_at=note.created_at
        )


# --- Endpoints ---

@router.get("/location/{location_id}", response_model=List[NoteResponse])
async def list_notes_for_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all notes for a specific location."""
    
    try:
        location_uuid = uuid.UUID(location_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location ID format"
        )
    
    # Verify location exists and user has access
    location = await get_location_by_id(db=db, location_id=location_uuid)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    if location.user_id != current_user.id and not location.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this location"
        )
    
    notes = await get_notes_by_location(db=db, location_id=location_uuid)
    return [NoteResponse.from_orm_note(note) for note in notes]


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_new_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new note for a location."""
    
    try:
        location_uuid = uuid.UUID(note_data.location_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location ID format"
        )
    
    # Verify location exists and user owns it
    location = await get_location_by_id(db=db, location_id=location_uuid)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    if location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add notes to this location"
        )
    
    note = await create_note(
        db=db,
        note_id=uuid.uuid4(),
        location_id=location_uuid,
        content=note_data.content
    )
    
    # Set the name field
    note.name = note_data.name
    await db.commit()
    await db.refresh(note)
    
    return NoteResponse.from_orm_note(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note."""
    
    try:
        note_uuid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    # Get note
    from sqlalchemy import select
    result = await db.execute(select(Note).where(Note.id == note_uuid))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Verify ownership through location
    location = await get_location_by_id(db=db, location_id=note.location_id)
    if not location or location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note"
        )
    
    await db.delete(note)
    await db.commit()
    
    return None
