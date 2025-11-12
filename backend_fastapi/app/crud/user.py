"""CRUD operations for User model."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..core.security import get_password_hash


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get a user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(password)
    
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_user(db: AsyncSession, user: User, **kwargs) -> User:
    """Update user fields."""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    """Delete a user."""
    await db.delete(user)
    await db.commit()
