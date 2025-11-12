"""CRUD operations for integrations."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..models.integrations import ImmichIntegration, StravaToken, WandererIntegration


# ============================================================================
# IMMICH INTEGRATION CRUD
# ============================================================================

async def create_immich_integration(
    db: AsyncSession,
    user_id: int,
    server_url: str,
    api_key: str,
    copy_locally: bool = True,
) -> ImmichIntegration:
    """Create Immich integration."""
    integration = ImmichIntegration(
        user_id=user_id,
        server_url=server_url,
        api_key=api_key,
        copy_locally=copy_locally,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return integration


async def get_immich_integration_by_id(
    db: AsyncSession, integration_id: UUID, user_id: int
) -> Optional[ImmichIntegration]:
    """Get Immich integration by ID."""
    result = await db.execute(
        select(ImmichIntegration).where(
            and_(
                ImmichIntegration.id == integration_id,
                ImmichIntegration.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_immich_integrations(
    db: AsyncSession, user_id: int
) -> List[ImmichIntegration]:
    """Get all Immich integrations for user."""
    result = await db.execute(
        select(ImmichIntegration)
        .where(ImmichIntegration.user_id == user_id)
        .order_by(ImmichIntegration.created_at.desc())
    )
    return list(result.scalars().all())


async def update_immich_integration(
    db: AsyncSession,
    integration_id: UUID,
    user_id: int,
    server_url: Optional[str] = None,
    api_key: Optional[str] = None,
    copy_locally: Optional[bool] = None,
) -> Optional[ImmichIntegration]:
    """Update Immich integration."""
    integration = await get_immich_integration_by_id(db, integration_id, user_id)
    if not integration:
        return None
    
    if server_url is not None:
        integration.server_url = server_url
    if api_key is not None:
        integration.api_key = api_key
    if copy_locally is not None:
        integration.copy_locally = copy_locally
    
    await db.flush()
    await db.refresh(integration)
    return integration


async def delete_immich_integration(
    db: AsyncSession, integration_id: UUID, user_id: int
) -> bool:
    """Delete Immich integration."""
    integration = await get_immich_integration_by_id(db, integration_id, user_id)
    if not integration:
        return False
    
    await db.delete(integration)
    await db.flush()
    return True


# ============================================================================
# STRAVA TOKEN CRUD
# ============================================================================

async def create_strava_token(
    db: AsyncSession,
    user_id: int,
    access_token: str,
    refresh_token: str,
    expires_at: int,
    athlete_id: Optional[int] = None,
    scope: Optional[str] = None,
) -> StravaToken:
    """Create or update Strava token."""
    # Check if token exists
    result = await db.execute(
        select(StravaToken).where(StravaToken.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.expires_at = expires_at
        if athlete_id is not None:
            existing.athlete_id = athlete_id
        if scope is not None:
            existing.scope = scope
        await db.flush()
        await db.refresh(existing)
        return existing
    else:
        # Create new
        token = StravaToken(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            athlete_id=athlete_id,
            scope=scope,
        )
        db.add(token)
        await db.flush()
        await db.refresh(token)
        return token


async def get_strava_token(db: AsyncSession, user_id: int) -> Optional[StravaToken]:
    """Get Strava token for user."""
    result = await db.execute(
        select(StravaToken).where(StravaToken.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_strava_token(db: AsyncSession, user_id: int) -> bool:
    """Delete Strava token."""
    token = await get_strava_token(db, user_id)
    if not token:
        return False
    
    await db.delete(token)
    await db.flush()
    return True


# ============================================================================
# WANDERER INTEGRATION CRUD
# ============================================================================

async def create_wanderer_integration(
    db: AsyncSession,
    user_id: int,
    server_url: str,
    username: str,
    token: Optional[str] = None,
    token_expiry: Optional[str] = None,
) -> WandererIntegration:
    """Create Wanderer integration."""
    integration = WandererIntegration(
        user_id=user_id,
        server_url=server_url,
        username=username,
        token=token,
        token_expiry=token_expiry,
    )
    db.add(integration)
    await db.flush()
    await db.refresh(integration)
    return integration


async def get_wanderer_integration_by_id(
    db: AsyncSession, integration_id: UUID, user_id: int
) -> Optional[WandererIntegration]:
    """Get Wanderer integration by ID."""
    result = await db.execute(
        select(WandererIntegration).where(
            and_(
                WandererIntegration.id == integration_id,
                WandererIntegration.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_wanderer_integrations(
    db: AsyncSession, user_id: int
) -> List[WandererIntegration]:
    """Get all Wanderer integrations for user."""
    result = await db.execute(
        select(WandererIntegration)
        .where(WandererIntegration.user_id == user_id)
        .order_by(WandererIntegration.created_at.desc())
    )
    return list(result.scalars().all())


async def update_wanderer_integration(
    db: AsyncSession,
    integration_id: UUID,
    user_id: int,
    server_url: Optional[str] = None,
    username: Optional[str] = None,
    token: Optional[str] = None,
    token_expiry: Optional[str] = None,
) -> Optional[WandererIntegration]:
    """Update Wanderer integration."""
    integration = await get_wanderer_integration_by_id(db, integration_id, user_id)
    if not integration:
        return None
    
    if server_url is not None:
        integration.server_url = server_url
    if username is not None:
        integration.username = username
    if token is not None:
        integration.token = token
    if token_expiry is not None:
        integration.token_expiry = token_expiry
    
    await db.flush()
    await db.refresh(integration)
    return integration


async def delete_wanderer_integration(
    db: AsyncSession, integration_id: UUID, user_id: int
) -> bool:
    """Delete Wanderer integration."""
    integration = await get_wanderer_integration_by_id(db, integration_id, user_id)
    if not integration:
        return False
    
    await db.delete(integration)
    await db.flush()
    return True
