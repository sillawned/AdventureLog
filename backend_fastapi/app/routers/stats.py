"""Statistics and dashboard router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.base import get_db
from app.models.adventure import Location, Visit, Collection, Note
from app.models.user import User
from app.deps import get_current_user

router = APIRouter()


# --- Schemas ---

class StatsResponse(BaseModel):
    """Schema for user statistics."""
    total_locations: int
    total_collections: int
    total_visits: int
    total_notes: int
    public_locations: int
    top_rated_locations: int


# --- Endpoints ---

@router.get("/", response_model=StatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for the current user."""
    
    # Count locations
    total_locations_result = await db.execute(
        select(func.count(Location.id)).where(Location.user_id == current_user.id)
    )
    total_locations = total_locations_result.scalar() or 0
    
    # Count public locations
    public_locations_result = await db.execute(
        select(func.count(Location.id)).where(
            Location.user_id == current_user.id,
            Location.is_public == True
        )
    )
    public_locations = public_locations_result.scalar() or 0
    
    # Count collections
    total_collections_result = await db.execute(
        select(func.count(Collection.id)).where(Collection.user_id == current_user.id)
    )
    total_collections = total_collections_result.scalar() or 0
    
    # Count visits (through user's locations)
    total_visits_result = await db.execute(
        select(func.count(Visit.id)).join(Location).where(Location.user_id == current_user.id)
    )
    total_visits = total_visits_result.scalar() or 0
    
    # Count notes (through user's locations)
    total_notes_result = await db.execute(
        select(func.count(Note.id)).join(Location).where(Location.user_id == current_user.id)
    )
    total_notes = total_notes_result.scalar() or 0
    
    # Count top-rated locations (rating >= 4)
    top_rated_result = await db.execute(
        select(func.count(Location.id)).where(
            Location.user_id == current_user.id,
            Location.rating >= 4
        )
    )
    top_rated_locations = top_rated_result.scalar() or 0
    
    return StatsResponse(
        total_locations=total_locations,
        total_collections=total_collections,
        total_visits=total_visits,
        total_notes=total_notes,
        public_locations=public_locations,
        top_rated_locations=top_rated_locations
    )
