"""Categories CRUD router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import get_db
from app.models.adventure import Category
from app.models.user import User
from app.deps import get_current_user
from app.crud.adventure import get_categories_by_user, get_category_by_id

router = APIRouter()


# --- Schemas ---

class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    user_id: int
    name: str
    icon: Optional[str]
    color: Optional[str]

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all categories for the current user."""
    categories = await get_categories_by_user(db=db, user_id=current_user.id)
    return categories


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category."""
    
    category = Category(
        user_id=current_user.id,
        name=category_data.name,
        icon=category_data.icon,
        color=category_data.color
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a category."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this category"
        )
    
    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a category."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this category"
        )
    
    await db.delete(category)
    await db.commit()
    
    return None
