"""Authentication router with local user registration and JWT tokens."""
from __future__ import annotations

from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_username, get_user_by_email, create_user
from app.models.base import get_db
from app.models.user import User
from app.core.security import create_access_token, decode_access_token, verify_password
from app.deps import get_current_user
from app.core.config import settings

router = APIRouter()


# --- Schemas ---
class UserRegister(BaseModel):
    """User registration payload."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "bearer"


# --- Endpoints ---
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user with local authentication."""
    # Check if username exists
    existing_user = await get_user_by_username(db, payload.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = await get_user_by_email(db, payload.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await create_user(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name
    )
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/token", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 password flow login. Returns JWT token and sets HttpOnly cookie."""
    # Look up user
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    # Set HttpOnly cookie
    cookie_name = settings.ACCESS_TOKEN_COOKIE_NAME
    max_age = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    response.set_cookie(
        cookie_name,
        access_token,
        max_age=max_age,
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE,
        path=settings.ACCESS_TOKEN_COOKIE_PATH,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """Clear the access token cookie."""
    cookie_name = settings.ACCESS_TOKEN_COOKIE_NAME
    response.delete_cookie(
        cookie_name,
        path=settings.ACCESS_TOKEN_COOKIE_PATH,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
