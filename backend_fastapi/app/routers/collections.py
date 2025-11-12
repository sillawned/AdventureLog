"""Collections CRUD router."""

import uuid
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.adventure import Collection
from app.models.user import User
from app.deps import get_current_user
from app.crud.adventure import (
    get_collection_by_id,
    get_collections_by_user,
    create_collection,
    search_collections,
)

router = APIRouter()


# --- Schemas ---

class CollectionCreate(BaseModel):
    """Schema for creating a collection."""
    name: str
    is_public: bool = False
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    link: Optional[str] = None


class CollectionUpdate(BaseModel):
    """Schema for updating a collection."""
    name: Optional[str] = None
    is_archived: Optional[bool] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    link: Optional[str] = None


class CollectionResponse(BaseModel):
    """Schema for collection response."""
    id: str
    user_id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    link: Optional[str]
    is_archived: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]

    @classmethod
    def from_orm_collection(cls, collection: Collection) -> "CollectionResponse":
        """Create response from ORM Collection object."""
        return cls(
            id=str(collection.id),
            user_id=collection.user_id,
            name=collection.name,
            description=collection.description,
            start_date=collection.start_date,
            end_date=collection.end_date,
            link=collection.link,
            is_archived=collection.is_archived,
            is_public=collection.is_public,
            created_at=collection.created_at,
            updated_at=collection.updated_at
        )

    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """Schema for paginated collection list."""
    total: int
    collections: List[CollectionResponse]


# --- Endpoints ---

@router.get("/", response_model=CollectionListResponse)
async def list_collections(
    limit: int = Query(default=100, le=100),
    offset: int = Query(default=0, ge=0),
    include_archived: bool = Query(default=False),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all collections for the current user."""
    
    if search:
        collections = await search_collections(
            db=db,
            user_id=current_user.id,
            search_term=search,
            limit=limit
        )
        total = len(collections)
    else:
        collections = await get_collections_by_user(
            db=db,
            user_id=current_user.id,
            include_archived=include_archived,
            limit=limit,
            offset=offset
        )
        total = len(collections)  # TODO: Add count function
    
    return CollectionListResponse(
        total=total,
        collections=[CollectionResponse.from_orm_collection(col) for col in collections]
    )


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_new_collection(
    collection_data: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new collection."""
    
    collection = await create_collection(
        db=db,
        collection_id=uuid.uuid4(),
        user_id=current_user.id,
        name=collection_data.name,
        is_public=collection_data.is_public,
        description=collection_data.description,
        start_date=collection_data.start_date,
        end_date=collection_data.end_date,
        link=collection_data.link,
    )
    
    await db.commit()
    
    return CollectionResponse.from_orm_collection(collection)


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific collection by ID."""
    
    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection ID format"
        )
    
    collection = await get_collection_by_id(db=db, collection_id=collection_uuid)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check ownership or public access
    if collection.user_id != current_user.id and not collection.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this collection"
        )
    
    return CollectionResponse.from_orm_collection(collection)


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_existing_collection(
    collection_id: str,
    collection_data: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a collection."""
    
    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection ID format"
        )
    
    collection = await get_collection_by_id(db=db, collection_id=collection_uuid)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check ownership
    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this collection"
        )
    
    # Update fields
    update_data = collection_data.model_dump(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(collection, key, value)
        await db.commit()
        await db.refresh(collection)
    
    return CollectionResponse.from_orm_collection(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a collection."""
    
    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection ID format"
        )
    
    collection = await get_collection_by_id(db=db, collection_id=collection_uuid)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check ownership
    if collection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this collection"
        )
    
    await db.delete(collection)
    await db.commit()
    
    return None
