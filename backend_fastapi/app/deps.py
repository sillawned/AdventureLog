"""FastAPI dependencies for authentication and database access."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.models.base import get_db
from app.models.user import User
from app.crud.user import get_user_by_username as crud_get_user_by_username
from app.core.config import settings
from typing import Optional


async def _get_token_from_request(request: Request) -> Optional[str]:
    """Extract bearer token from Authorization header or cookie."""
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]

    # Fallback to cookie
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    return token


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.
    
    Supports both Bearer token in Authorization header and HttpOnly cookie.
    Raises 401 if token is invalid or user not found.
    """
    token = await _get_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = await crud_get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user. Raises 403 if user is inactive."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser. Raises 403 if user is not a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user


async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """Try to get current user from token. Returns None if no valid token."""
    token = await _get_token_from_request(request)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    # Lookup user in DB
    user = await crud_get_user_by_username(db, username)
    return user

