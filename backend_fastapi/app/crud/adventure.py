"""CRUD operations for adventure domain models."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from ..models.adventure import (
    Location, Visit, Collection, Category,
    Note, Checklist, Activity
)


# ============================================================================
# VISIT CRUD
# ============================================================================

async def get_visit_by_id(db: AsyncSession, visit_id: UUID) -> Optional[Visit]:
    """Get a visit by ID with its location relationship loaded."""
    result = await db.execute(
        select(Visit)
        .options(selectinload(Visit.location))
        .where(Visit.id == visit_id)
    )
    return result.scalar_one_or_none()


async def get_visits_by_user(
    db: AsyncSession,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[Visit]:
    """Get all visits for a user's locations."""
    result = await db.execute(
        select(Visit)
        .options(selectinload(Visit.location))
        .join(Location, Visit.location_id == Location.id)
        .where(Location.user_id == user_id)
        .order_by(Visit.start_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def count_visits_by_user(db: AsyncSession, user_id: int) -> int:
    """Count total visits for a user."""
    result = await db.execute(
        select(func.count(Visit.id))
        .join(Location, Visit.location_id == Location.id)
        .where(Location.user_id == user_id)
    )
    return result.scalar_one()


async def create_visit(
    db: AsyncSession,
    visit_id: UUID,
    location_id: UUID,
    start_date=None,
    end_date=None,
    timezone: Optional[str] = None,
    notes: Optional[str] = None,
) -> Visit:
    """Create a new visit."""
    visit = Visit(
        id=visit_id,
        location_id=location_id,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        notes=notes,
    )
    db.add(visit)
    await db.flush()
    await db.refresh(visit)
    return visit


async def update_visit(
    db: AsyncSession,
    visit: Visit,
    **kwargs
) -> Visit:
    """Update visit fields."""
    for key, value in kwargs.items():
        if hasattr(visit, key) and value is not None:
            setattr(visit, key, value)
    
    await db.flush()
    await db.refresh(visit)
    return visit


async def delete_visit(db: AsyncSession, visit: Visit) -> None:
    """Delete a visit."""
    await db.delete(visit)
    await db.flush()


# ============================================================================
# LOCATION CRUD
# ============================================================================

async def get_location_by_id(db: AsyncSession, location_id: UUID) -> Optional[Location]:
    """Get a location by ID."""
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.category), selectinload(Location.collection))
        .where(Location.id == location_id)
    )
    return result.scalar_one_or_none()


async def get_locations_by_user(
    db: AsyncSession,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[Location]:
    """Get all locations for a user."""
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.category), selectinload(Location.collection))
        .where(Location.user_id == user_id)
        .order_by(Location.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def search_locations(
    db: AsyncSession,
    user_id: int,
    search_term: str,
    limit: int = 50
) -> List[Location]:
    """Search locations using full-text search."""
    # PostgreSQL full-text search
    from sqlalchemy import func
    
    search_query = select(Location).options(
        selectinload(Location.category), 
        selectinload(Location.collection)
    ).where(
        and_(
            Location.user_id == user_id,
            func.to_tsvector('english',
                func.coalesce(Location.name, '') + ' ' +
                func.coalesce(Location.description, '') + ' ' +
                func.coalesce(Location.address, '') + ' ' +
                func.coalesce(Location.city, '') + ' ' +
                func.coalesce(Location.state, '') + ' ' +
                func.coalesce(Location.country, '')
            ).op('@@')(func.plainto_tsquery('english', search_term))
        )
    ).limit(limit)
    
    result = await db.execute(search_query)
    return list(result.scalars().all())


async def create_location(
    db: AsyncSession,
    location_id: UUID,
    user_id: int,
    name: str,
    **kwargs
) -> Location:
    """Create a new location."""
    location = Location(
        id=location_id,
        user_id=user_id,
        name=name,
        **kwargs
    )
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return location


async def update_location(db: AsyncSession, location: Location, **kwargs) -> Location:
    """Update location fields."""
    for key, value in kwargs.items():
        if hasattr(location, key) and value is not None:
            setattr(location, key, value)
    
    await db.flush()
    await db.refresh(location)
    return location


async def delete_location(db: AsyncSession, location: Location) -> None:
    """Delete a location and all related data."""
    await db.delete(location)
    await db.flush()


async def get_user_locations(
    db: AsyncSession,
    user_id: int,
    limit: int = 1000,
    offset: int = 0
) -> List[Location]:
    """Get all locations for a user with relationships loaded."""
    result = await db.execute(
        select(Location)
        .options(
            selectinload(Location.category),
            selectinload(Location.collection),
            selectinload(Location.visits)
        )
        .where(Location.user_id == user_id)
        .order_by(Location.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_public_locations(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0
) -> List[Location]:
    """Get all public locations."""
    result = await db.execute(
        select(Location)
        .options(selectinload(Location.category), selectinload(Location.collection))
        .where(Location.is_public.is_(True))
        .order_by(Location.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_user_locations_excluding_collections(
    db: AsyncSession,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> List[Location]:
    """Get user locations that are not in any collection.
    
    Note: This is a simplified version. For proper M2M handling,
    we'd need the association table model.
    """
    result = await db.execute(
        select(Location)
        .where(Location.user_id == user_id)
        .order_by(Location.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def count_locations(
    db: AsyncSession,
    user_id: Optional[int] = None,
    is_public: Optional[bool] = None
) -> int:
    """Count locations with optional filters."""
    query = select(func.count(Location.id))
    
    conditions = []
    if user_id is not None:
        conditions.append(Location.user_id == user_id)
    if is_public is not None:
        conditions.append(Location.is_public == is_public)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    return result.scalar() or 0


# ============================================================================
# COLLECTION CRUD
# ============================================================================

async def get_collection_by_id(db: AsyncSession, collection_id: UUID) -> Optional[Collection]:
    """Get a collection by ID."""
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    return result.scalar_one_or_none()


async def get_user_collections(
    db: AsyncSession,
    user_id: int,
    include_archived: bool = True,
    limit: int = 1000,
    offset: int = 0
) -> List[Collection]:
    """Get all collections for a user (alias for get_collections_by_user)."""
    return await get_collections_by_user(db, user_id, include_archived, limit, offset)


async def get_collections_by_user(
    db: AsyncSession,
    user_id: int,
    include_archived: bool = False,
    limit: int = 100,
    offset: int = 0
) -> List[Collection]:
    """Get collections for a user."""
    query = select(Collection).where(Collection.user_id == user_id)
    
    if not include_archived:
        query = query.where(Collection.is_archived.is_(False))
    
    query = query.order_by(Collection.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_collections(
    db: AsyncSession,
    user_id: int,
    search_term: str,
    limit: int = 50
) -> List[Collection]:
    """Search collections by name."""
    result = await db.execute(
        select(Collection)
        .where(
            and_(
                Collection.user_id == user_id,
                Collection.name.ilike(f"%{search_term}%")
            )
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_collection(
    db: AsyncSession,
    collection_id: UUID,
    user_id: int,
    name: str,
    **kwargs
) -> Collection:
    """Create a new collection."""
    collection = Collection(
        id=collection_id,
        user_id=user_id,
        name=name,
        **kwargs
    )
    db.add(collection)
    await db.flush()
    await db.refresh(collection)
    return collection


# ============================================================================
# CATEGORY CRUD
# ============================================================================

async def get_user_categories(db: AsyncSession, user_id: int) -> List[Category]:
    """Get all categories for a user (alias for get_categories_by_user)."""
    return await get_categories_by_user(db, user_id)


async def get_categories_by_user(db: AsyncSession, user_id: int) -> List[Category]:
    """Get all categories for a user."""
    result = await db.execute(
        select(Category)
        .where(Category.user_id == user_id)
        .order_by(Category.name)
    )
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> Optional[Category]:
    """Get a category by ID."""
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()


async def create_category(
    db: AsyncSession,
    user_id: int,
    name: str,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> Category:
    """Create a new category."""
    category = Category(
        user_id=user_id,
        name=name,
        icon=icon,
        color=color,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


# ============================================================================
# NOTE CRUD
# ============================================================================

async def get_notes_by_location(db: AsyncSession, location_id: UUID) -> List[Note]:
    """Get all notes for a location."""
    result = await db.execute(
        select(Note)
        .where(Note.location_id == location_id)
        .order_by(Note.created_at.desc())
    )
    return list(result.scalars().all())


async def create_note(
    db: AsyncSession,
    note_id: UUID,
    location_id: UUID,
    content: str
) -> Note:
    """Create a new note."""
    note = Note(
        id=note_id,
        location_id=location_id,
        content=content
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


# ============================================================================
# ACTIVITY CRUD
# ============================================================================

async def get_activities_by_location(db: AsyncSession, location_id: UUID) -> List[Activity]:
    """Get all activities for a location."""
    result = await db.execute(
        select(Activity)
        .where(Activity.location_id == location_id)
        .order_by(Activity.created_at.desc())
    )
    return list(result.scalars().all())


# ============================================================================
# CHECKLIST CRUD
# ============================================================================

async def get_checklists_by_location(
    db: AsyncSession,
    location_id: UUID
) -> List[Checklist]:
    """Get all checklists for a location with their items."""
    result = await db.execute(
        select(Checklist)
        .options(selectinload(Checklist.items))
        .where(Checklist.location_id == location_id)
        .order_by(Checklist.created_at.desc())
    )
    return list(result.scalars().all())
