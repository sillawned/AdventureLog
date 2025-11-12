"""CRUD operations for worldtravel models."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.worldtravel import Country, Region, City, VisitedRegion, VisitedCity


# ============================================================================
# COUNTRY CRUD
# ============================================================================

async def get_countries(
    db: AsyncSession,
    limit: int = 300,
    offset: int = 0
) -> List[Country]:
    """Get all countries ordered by name."""
    result = await db.execute(
        select(Country)
        .order_by(Country.name)
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_country_by_code(db: AsyncSession, country_code: str) -> Optional[Country]:
    """Get country by ISO2 code."""
    result = await db.execute(
        select(Country).where(Country.country_code == country_code.upper())
    )
    return result.scalar_one_or_none()


async def count_countries(db: AsyncSession) -> int:
    """Count total countries."""
    result = await db.execute(select(func.count(Country.id)))
    return result.scalar() or 0


# ============================================================================
# REGION CRUD
# ============================================================================

async def get_regions_by_country(
    db: AsyncSession,
    country_code: str,
    limit: int = 500
) -> List[Region]:
    """Get regions for a country."""
    country = await get_country_by_code(db, country_code)
    if not country:
        return []
    
    result = await db.execute(
        select(Region)
        .where(Region.country_id == country.id)
        .order_by(Region.name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_region_by_id(db: AsyncSession, region_id: str) -> Optional[Region]:
    """Get region by ID with country loaded."""
    result = await db.execute(
        select(Region)
        .options(selectinload(Region.country))
        .where(Region.id == region_id)
    )
    return result.scalar_one_or_none()


# ============================================================================
# CITY CRUD
# ============================================================================

async def get_cities_by_region(
    db: AsyncSession,
    region_id: str,
    limit: int = 1000
) -> List[City]:
    """Get cities for a region."""
    result = await db.execute(
        select(City)
        .where(City.region_id == region_id)
        .order_by(City.name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_city_by_id(db: AsyncSession, city_id: str) -> Optional[City]:
    """Get city by ID with region/country loaded."""
    result = await db.execute(
        select(City)
        .options(
            selectinload(City.region).selectinload(Region.country)
        )
        .where(City.id == city_id)
    )
    return result.scalar_one_or_none()


# ============================================================================
# VISITED REGION CRUD
# ============================================================================

async def get_visited_regions(
    db: AsyncSession,
    user_id: int,
    country_code: Optional[str] = None
) -> List[VisitedRegion]:
    """Get user's visited regions, optionally filtered by country."""
    query = select(VisitedRegion).where(VisitedRegion.user_id == user_id)
    
    if country_code:
        country = await get_country_by_code(db, country_code)
        if country:
            query = query.join(Region).where(Region.country_id == country.id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_visited_region(
    db: AsyncSession,
    user_id: int,
    region_id: str
) -> Optional[VisitedRegion]:
    """Create visited region if not exists."""
    # Check if already visited
    existing = await db.execute(
        select(VisitedRegion).where(
            VisitedRegion.user_id == user_id,
            VisitedRegion.region_id == region_id
        )
    )
    if existing.scalar_one_or_none():
        return None
    
    visited = VisitedRegion(user_id=user_id, region_id=region_id)
    db.add(visited)
    await db.flush()
    await db.refresh(visited)
    return visited


async def delete_visited_region(
    db: AsyncSession,
    user_id: int,
    region_id: str
) -> bool:
    """Delete visited region."""
    result = await db.execute(
        select(VisitedRegion).where(
            VisitedRegion.user_id == user_id,
            VisitedRegion.region_id == region_id
        )
    )
    visited = result.scalar_one_or_none()
    if not visited:
        return False
    
    await db.delete(visited)
    await db.flush()
    return True


async def count_visited_regions_by_country(
    db: AsyncSession,
    user_id: int,
    country_id: int
) -> int:
    """Count visited regions in a country."""
    result = await db.execute(
        select(func.count(VisitedRegion.id))
        .join(Region)
        .where(
            VisitedRegion.user_id == user_id,
            Region.country_id == country_id
        )
    )
    return result.scalar() or 0


# ============================================================================
# VISITED CITY CRUD
# ============================================================================

async def get_visited_cities(
    db: AsyncSession,
    user_id: int,
    region_id: Optional[str] = None
) -> List[VisitedCity]:
    """Get user's visited cities, optionally filtered by region."""
    query = select(VisitedCity).where(VisitedCity.user_id == user_id)
    
    if region_id:
        query = query.join(City).where(City.region_id == region_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_visited_city(
    db: AsyncSession,
    user_id: int,
    city_id: str
) -> Optional[VisitedCity]:
    """Create visited city and auto-mark region if needed."""
    # Check if already visited
    existing = await db.execute(
        select(VisitedCity).where(
            VisitedCity.user_id == user_id,
            VisitedCity.city_id == city_id
        )
    )
    if existing.scalar_one_or_none():
        return None
    
    # Get city to find region
    city = await get_city_by_id(db, city_id)
    if not city:
        return None
    
    # Create visited city
    visited_city = VisitedCity(user_id=user_id, city_id=city_id)
    db.add(visited_city)
    
    # Auto-create visited region if not exists
    await create_visited_region(db, user_id, city.region_id)
    
    await db.flush()
    await db.refresh(visited_city)
    return visited_city


async def delete_visited_city(
    db: AsyncSession,
    user_id: int,
    city_id: str
) -> bool:
    """Delete visited city."""
    result = await db.execute(
        select(VisitedCity).where(
            VisitedCity.user_id == user_id,
            VisitedCity.city_id == city_id
        )
    )
    visited = result.scalar_one_or_none()
    if not visited:
        return False
    
    await db.delete(visited)
    await db.flush()
    return True
