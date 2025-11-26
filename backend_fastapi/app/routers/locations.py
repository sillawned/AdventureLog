"""Locations CRUD router."""

import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.adventure import Location
from app.models.user import User
from app.deps import get_current_user
from app.crud.adventure import (
    get_location_by_id,
    get_locations_by_user,
    create_location,
    update_location,
    delete_location,
    search_locations,
    count_locations,
    get_public_locations,
)

router = APIRouter()


# --- Schemas ---

class LocationCreate(BaseModel):
    """Schema for creating a new location."""
    name: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[int] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    link: Optional[str] = None
    category: Optional[int] = None  # category_id
    collection: Optional[str] = None  # collection_id (UUID as string)


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[int] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    link: Optional[str] = None
    category: Optional[int] = None  # category_id
    collection: Optional[str] = None  # collection_id (UUID as string)


class CategoryData(BaseModel):
    """Nested category data for location response."""
    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    
    class Config:
        from_attributes = True


class CollectionData(BaseModel):
    """Nested collection data for location response."""
    id: str
    name: str
    is_archived: bool
    is_public: bool
    
    class Config:
        from_attributes = True


class LocationResponse(BaseModel):
    """Schema for location response."""
    id: str
    user_id: int
    name: str
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    rating: Optional[int]
    tags: Optional[List[str]]
    is_public: bool
    link: Optional[str]
    category: Optional[CategoryData]
    collection: Optional[CollectionData]
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_orm_location(cls, location: Location) -> "LocationResponse":
        """Create response from ORM Location object."""
        category_data = None
        if location.category:
            category_data = CategoryData(
                id=location.category.id,
                name=location.category.name,
                icon=location.category.icon,
                color=location.category.color
            )
        
        collection_data = None
        if location.collection:
            collection_data = CollectionData(
                id=str(location.collection.id),
                name=location.collection.name,
                is_archived=location.collection.is_archived,
                is_public=location.collection.is_public
            )
        
        return cls(
            id=str(location.id),
            user_id=location.user_id,
            name=location.name,
            description=location.description,
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            city=location.city,
            state=location.state,
            country=location.country,
            rating=location.rating,
            tags=location.tags,
            is_public=location.is_public,
            link=location.link,
            category=category_data,
            collection=collection_data,
            created_at=location.created_at,
            updated_at=location.updated_at
        )

    class Config:
        from_attributes = True


class LocationListResponse(BaseModel):
    """Schema for paginated location list."""
    total: int
    locations: List[LocationResponse]


# --- Endpoints ---

@router.get("/", response_model=LocationListResponse)
async def list_locations(
    limit: int = Query(default=100, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all locations for the current user with optional search."""
    
    if search:
        locations = await search_locations(
            db=db,
            user_id=current_user.id,
            search_term=search,
            limit=limit
        )
        total = len(locations)
    else:
        locations = await get_locations_by_user(
            db=db,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        total = await count_locations(db=db, user_id=current_user.id)
    
    return LocationListResponse(
        total=total,
        locations=[LocationResponse.from_orm_location(loc) for loc in locations]
    )


@router.get("/public", response_model=LocationListResponse)
async def list_public_locations(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all public locations (no authentication required)."""
    
    locations = await get_public_locations(
        db=db,
        limit=limit,
        offset=offset
    )
    total = await count_locations(db=db, is_public=True)
    
    return LocationListResponse(
        total=total,
        locations=[LocationResponse.from_orm_location(loc) for loc in locations]
    )


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new location."""
    
    location = await create_location(
        db=db,
        location_id=uuid.uuid4(),
        user_id=current_user.id,
        name=location_data.name,
        description=location_data.description,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        address=location_data.address,
        city=location_data.city,
        state=location_data.state,
        country=location_data.country,
        rating=location_data.rating,
        tags=location_data.tags,
        is_public=location_data.is_public,
        link=location_data.link,
        category_id=location_data.category,
        collection_id=uuid.UUID(location_data.collection) if location_data.collection else None,
    )
    
    await db.commit()
    
    return LocationResponse.from_orm_location(location)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific location by ID."""
    
    try:
        location_uuid = uuid.UUID(location_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location ID format"
        )
    
    location = await get_location_by_id(db=db, location_id=location_uuid)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Check ownership or public access
    if location.user_id != current_user.id and not location.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this location"
        )
    
    return LocationResponse.from_orm_location(location)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_existing_location(
    location_id: str,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a location."""
    
    try:
        location_uuid = uuid.UUID(location_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location ID format"
        )
    
    location = await get_location_by_id(db=db, location_id=location_uuid)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Check ownership
    if location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this location"
        )
    
    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    if update_data:
        # Convert category and collection to proper types with validation
        if 'category' in update_data:
            # category may be None or int
            category_val = update_data.pop('category')
            if category_val is not None:
                if not isinstance(category_val, int):
                    raise HTTPException(status_code=400, detail="Invalid category format")
                update_data['category_id'] = category_val
            else:
                update_data['category_id'] = None
        if 'collection' in update_data:
            raw_collection = update_data.pop('collection')
            if raw_collection in (None, ""):
                update_data['collection_id'] = None  # Allow clearing collection
            else:
                try:
                    update_data['collection_id'] = uuid.UUID(str(raw_collection))
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail="Invalid collection UUID format")

        # Perform update
        try:
            location = await update_location(db=db, location=location, **update_data)
            await db.commit()
        except Exception as e:
            # Rollback and surface a cleaner error instead of 500
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Update failed: {e}")
    
    return LocationResponse.from_orm_location(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a location."""
    
    try:
        location_uuid = uuid.UUID(location_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid location ID format"
        )
    
    location = await get_location_by_id(db=db, location_id=location_uuid)
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Check ownership
    if location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this location"
        )
    
    await delete_location(db=db, location=location)
    await db.commit()
    
    return None


