"""WorldTravel router - countries, regions, cities, and visited tracking."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal

from app.models.base import get_db
from app.models.user import User
from app.deps import get_current_user
from app.crud.worldtravel import (
    get_countries,
    get_country_by_code,
    get_regions_by_country,
    get_region_by_id,
    get_cities_by_region,
    get_city_by_id,
    get_visited_regions,
    create_visited_region,
    delete_visited_region,
    count_visited_regions_by_country,
    get_visited_cities,
    create_visited_city,
    delete_visited_city,
)

router = APIRouter()


# --- Schemas ---

class CountryResponse(BaseModel):
    """Country response schema."""
    id: int
    name: str
    country_code: str
    subregion: Optional[str]
    capital: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    num_regions: int = 0
    num_visits: int = 0
    
    class Config:
        from_attributes = True


class RegionResponse(BaseModel):
    """Region response schema."""
    id: str
    name: str
    country_id: int
    country_name: Optional[str] = None
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    num_cities: int = 0
    
    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    """City response schema."""
    id: str
    name: str
    region_id: str
    region_name: Optional[str] = None
    country_name: Optional[str] = None
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    
    class Config:
        from_attributes = True


class VisitedRegionCreate(BaseModel):
    """Schema for marking region as visited."""
    region: str  # region_id


class VisitedRegionResponse(BaseModel):
    """Visited region response."""
    id: int
    region: str  # region_id
    name: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class VisitedCityCreate(BaseModel):
    """Schema for marking city as visited."""
    city: str  # city_id


class VisitedCityResponse(BaseModel):
    """Visited city response."""
    id: int
    city: str  # city_id
    name: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# --- Country Endpoints ---

@router.get("/countries/", response_model=List[CountryResponse])
async def list_countries(
    limit: int = Query(default=300, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all countries with visit counts."""
    countries = await get_countries(db, limit, offset)
    
    # Enrich with counts
    result = []
    for country in countries:
        num_visits = await count_visited_regions_by_country(db, current_user.id, country.id)
        # Count regions - load from relationship
        from sqlalchemy import select, func
        from app.models.worldtravel import Region
        region_count = await db.execute(
            select(func.count(Region.id)).where(Region.country_id == country.id)
        )
        num_regions = region_count.scalar() or 0
        
        result.append(CountryResponse(
            id=country.id,
            name=country.name,
            country_code=country.country_code,
            subregion=country.subregion,
            capital=country.capital,
            latitude=country.latitude,
            longitude=country.longitude,
            num_regions=num_regions,
            num_visits=num_visits
        ))
    
    return result


@router.get("/countries/{country_code}/regions/", response_model=List[RegionResponse])
async def list_regions_by_country(
    country_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get regions for a country."""
    country = await get_country_by_code(db, country_code)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    regions = await get_regions_by_country(db, country_code)
    
    # Enrich with city counts
    result = []
    for region in regions:
        from sqlalchemy import select, func
        from app.models.worldtravel import City
        city_count = await db.execute(
            select(func.count(City.id)).where(City.region_id == region.id)
        )
        num_cities = city_count.scalar() or 0
        
        result.append(RegionResponse(
            id=region.id,
            name=region.name,
            country_id=region.country_id,
            country_name=country.name,
            latitude=region.latitude,
            longitude=region.longitude,
            num_cities=num_cities
        ))
    
    return result


@router.get("/countries/{country_code}/visits/", response_model=List[VisitedRegionResponse])
async def list_visits_by_country(
    country_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's visited regions in a country."""
    visited = await get_visited_regions(db, current_user.id, country_code)
    
    result = []
    for v in visited:
        region = await get_region_by_id(db, v.region_id)
        result.append(VisitedRegionResponse(
            id=v.id,
            region=v.region_id,
            name=region.name if region else None,
            country_id=region.country_id if region else None,
            country_name=region.country.name if region and region.country else None,
            latitude=region.latitude if region else None,
            longitude=region.longitude if region else None
        ))
    
    return result


# --- Region Endpoints ---

@router.get("/regions/{region_id}/cities/", response_model=List[CityResponse])
async def list_cities_by_region(
    region_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get cities for a region."""
    region = await get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    cities = await get_cities_by_region(db, region_id)
    
    result = []
    for city in cities:
        result.append(CityResponse(
            id=city.id,
            name=city.name,
            region_id=city.region_id,
            region_name=region.name,
            country_name=region.country.name if region.country else None,
            latitude=city.latitude,
            longitude=city.longitude
        ))
    
    return result


@router.get("/regions/{region_id}/visits/", response_model=List[VisitedCityResponse])
async def list_visits_by_region(
    region_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's visited cities in a region."""
    visited = await get_visited_cities(db, current_user.id, region_id)
    
    result = []
    for v in visited:
        city = await get_city_by_id(db, v.city_id)
        result.append(VisitedCityResponse(
            id=v.id,
            city=v.city_id,
            name=city.name if city else None,
            latitude=city.latitude if city else None,
            longitude=city.longitude if city else None
        ))
    
    return result


# --- Visited Region Endpoints ---

@router.get("/visited-regions/", response_model=List[VisitedRegionResponse])
async def list_visited_regions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all visited regions for the user."""
    visited = await get_visited_regions(db, current_user.id)
    
    result = []
    for v in visited:
        region = await get_region_by_id(db, v.region_id)
        result.append(VisitedRegionResponse(
            id=v.id,
            region=v.region_id,
            name=region.name if region else None,
            country_id=region.country_id if region else None,
            country_name=region.country.name if region and region.country else None,
            latitude=region.latitude if region else None,
            longitude=region.longitude if region else None
        ))
    
    return result


@router.post("/visited-regions/", response_model=VisitedRegionResponse, status_code=status.HTTP_201_CREATED)
async def mark_region_visited(
    data: VisitedRegionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a region as visited."""
    # Verify region exists
    region = await get_region_by_id(db, data.region)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    visited = await create_visited_region(db, current_user.id, data.region)
    if not visited:
        raise HTTPException(status_code=400, detail="Region already marked as visited")
    
    await db.commit()
    
    return VisitedRegionResponse(
        id=visited.id,
        region=visited.region_id,
        name=region.name,
        country_id=region.country_id,
        country_name=region.country.name if region.country else None,
        latitude=region.latitude,
        longitude=region.longitude
    )


@router.delete("/visited-regions/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_region_visited(
    region_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove visited region."""
    success = await delete_visited_region(db, current_user.id, region_id)
    if not success:
        raise HTTPException(status_code=404, detail="Visited region not found")
    
    await db.commit()
    return None


# --- Visited City Endpoints ---

@router.get("/visited-cities/", response_model=List[VisitedCityResponse])
async def list_visited_cities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all visited cities for the user."""
    visited = await get_visited_cities(db, current_user.id)
    
    result = []
    for v in visited:
        city = await get_city_by_id(db, v.city_id)
        result.append(VisitedCityResponse(
            id=v.id,
            city=v.city_id,
            name=city.name if city else None,
            latitude=city.latitude if city else None,
            longitude=city.longitude if city else None
        ))
    
    return result


@router.post("/visited-cities/", response_model=VisitedCityResponse, status_code=status.HTTP_201_CREATED)
async def mark_city_visited(
    data: VisitedCityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a city as visited (auto-marks region too)."""
    # Verify city exists
    city = await get_city_by_id(db, data.city)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    visited = await create_visited_city(db, current_user.id, data.city)
    if not visited:
        raise HTTPException(status_code=400, detail="City already marked as visited")
    
    await db.commit()
    
    return VisitedCityResponse(
        id=visited.id,
        city=visited.city_id,
        name=city.name,
        latitude=city.latitude,
        longitude=city.longitude
    )


@router.delete("/visited-cities/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_city_visited(
    city_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove visited city."""
    success = await delete_visited_city(db, current_user.id, city_id)
    if not success:
        raise HTTPException(status_code=404, detail="Visited city not found")
    
    await db.commit()
    return None
