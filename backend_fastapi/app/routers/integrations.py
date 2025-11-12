"""Integrations router - manage external service integrations."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.models.base import get_db
from app.models.user import User
from app.deps import get_current_user
from app.crud.integrations import (
    create_immich_integration,
    get_immich_integration_by_id,
    get_user_immich_integrations,
    update_immich_integration,
    delete_immich_integration,
    create_strava_token,
    get_strava_token,
    delete_strava_token,
    create_wanderer_integration,
    get_wanderer_integration_by_id,
    get_user_wanderer_integrations,
    update_wanderer_integration,
    delete_wanderer_integration,
)

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

# Immich Schemas
class ImmichIntegrationCreate(BaseModel):
    """Create Immich integration."""
    server_url: str = Field(..., max_length=255)
    api_key: str = Field(..., max_length=255)
    copy_locally: bool = True


class ImmichIntegrationUpdate(BaseModel):
    """Update Immich integration."""
    server_url: Optional[str] = Field(None, max_length=255)
    api_key: Optional[str] = Field(None, max_length=255)
    copy_locally: Optional[bool] = None


class ImmichIntegrationResponse(BaseModel):
    """Immich integration response."""
    id: str
    server_url: str
    copy_locally: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Strava Schemas
class StravaTokenCreate(BaseModel):
    """Create/update Strava token."""
    access_token: str = Field(..., max_length=255)
    refresh_token: str = Field(..., max_length=255)
    expires_at: int  # Unix timestamp
    athlete_id: Optional[int] = None
    scope: Optional[str] = Field(None, max_length=255)


class StravaTokenResponse(BaseModel):
    """Strava token response."""
    id: int
    athlete_id: Optional[int] = None
    scope: Optional[str] = None
    expires_at: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Wanderer Schemas
class WandererIntegrationCreate(BaseModel):
    """Create Wanderer integration."""
    server_url: str = Field(..., max_length=255)
    username: str = Field(..., max_length=255)
    token: Optional[str] = Field(None, max_length=512)
    token_expiry: Optional[datetime] = None


class WandererIntegrationUpdate(BaseModel):
    """Update Wanderer integration."""
    server_url: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    token: Optional[str] = Field(None, max_length=512)
    token_expiry: Optional[datetime] = None


class WandererIntegrationResponse(BaseModel):
    """Wanderer integration response."""
    id: str
    server_url: str
    username: str
    token_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# IMMICH ENDPOINTS
# ============================================================================

@router.post("/immich/", response_model=ImmichIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_immich(
    data: ImmichIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Immich integration."""
    integration = await create_immich_integration(
        db=db,
        user_id=current_user.id,
        server_url=data.server_url,
        api_key=data.api_key,
        copy_locally=data.copy_locally,
    )
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/immich/", response_model=List[ImmichIntegrationResponse])
async def list_immich(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's Immich integrations."""
    integrations = await get_user_immich_integrations(db, current_user.id)
    return integrations


@router.get("/immich/{integration_id}", response_model=ImmichIntegrationResponse)
async def get_immich(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Immich integration by ID."""
    integration = await get_immich_integration_by_id(db, integration_id, current_user.id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/immich/{integration_id}", response_model=ImmichIntegrationResponse)
async def update_immich(
    integration_id: str,
    data: ImmichIntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update Immich integration."""
    integration = await update_immich_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id,
        server_url=data.server_url,
        api_key=data.api_key,
        copy_locally=data.copy_locally,
    )
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    await db.commit()
    await db.refresh(integration)
    return integration


@router.delete("/immich/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_immich(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete Immich integration."""
    success = await delete_immich_integration(db, integration_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    await db.commit()
    return None


# ============================================================================
# STRAVA ENDPOINTS
# ============================================================================

@router.post("/strava/", response_model=StravaTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_strava(
    data: StravaTokenCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update Strava token."""
    token = await create_strava_token(
        db=db,
        user_id=current_user.id,
        access_token=data.access_token,
        refresh_token=data.refresh_token,
        expires_at=data.expires_at,
        athlete_id=data.athlete_id,
        scope=data.scope,
    )
    await db.commit()
    await db.refresh(token)
    return token


@router.get("/strava/", response_model=StravaTokenResponse)
async def get_strava(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's Strava token."""
    token = await get_strava_token(db, current_user.id)
    if not token:
        raise HTTPException(status_code=404, detail="Strava not connected")
    return token


@router.delete("/strava/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strava(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete Strava connection."""
    success = await delete_strava_token(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Strava not connected")
    
    await db.commit()
    return None


# ============================================================================
# WANDERER ENDPOINTS
# ============================================================================

@router.post("/wanderer/", response_model=WandererIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_wanderer(
    data: WandererIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create Wanderer integration."""
    integration = await create_wanderer_integration(
        db=db,
        user_id=current_user.id,
        server_url=data.server_url,
        username=data.username,
        token=data.token,
        token_expiry=data.token_expiry,
    )
    await db.commit()
    await db.refresh(integration)
    return integration


@router.get("/wanderer/", response_model=List[WandererIntegrationResponse])
async def list_wanderer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's Wanderer integrations."""
    integrations = await get_user_wanderer_integrations(db, current_user.id)
    return integrations


@router.get("/wanderer/{integration_id}", response_model=WandererIntegrationResponse)
async def get_wanderer(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get Wanderer integration by ID."""
    integration = await get_wanderer_integration_by_id(db, integration_id, current_user.id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/wanderer/{integration_id}", response_model=WandererIntegrationResponse)
async def update_wanderer(
    integration_id: str,
    data: WandererIntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update Wanderer integration."""
    integration = await update_wanderer_integration(
        db=db,
        integration_id=integration_id,
        user_id=current_user.id,
        server_url=data.server_url,
        username=data.username,
        token=data.token,
        token_expiry=data.token_expiry,
    )
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    await db.commit()
    await db.refresh(integration)
    return integration


@router.delete("/wanderer/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wanderer(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete Wanderer integration."""
    success = await delete_wanderer_integration(db, integration_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    await db.commit()
    return None
