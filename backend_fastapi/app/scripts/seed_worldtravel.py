"""Seed worldtravel data from CDN source.

This script imports countries, regions (states), and cities from the
dr5hn/countries-states-cities-database dataset available via CDN.
"""
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.worldtravel import Country, Region, City
from app.core.config import settings

REMOTE_DATA_SOURCE_URL = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/tags/v3.0/json/"


async def fetch_json(url: str) -> dict:
    """Fetch JSON from URL."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def seed_countries(session: AsyncSession):
    """Import countries from CDN."""
    print("Fetching countries...")
    data = await fetch_json(f"{REMOTE_DATA_SOURCE_URL}/countries.json")
    
    countries_list = data if isinstance(data, list) else data.get('data', [])
    
    print(f"Importing {len(countries_list)} countries...")
    
    for item in countries_list:
        country = Country(
            name=item.get('name'),
            country_code=item.get('iso2'),
            subregion=item.get('subregion'),
            capital=item.get('capital'),
            latitude=item.get('latitude'),
            longitude=item.get('longitude')
        )
        session.add(country)
    
    await session.commit()
    print(f"✓ Imported {len(countries_list)} countries")


async def seed_regions(session: AsyncSession):
    """Import regions/states from CDN."""
    print("Fetching regions/states...")
    data = await fetch_json(f"{REMOTE_DATA_SOURCE_URL}/states.json")
    
    regions_list = data if isinstance(data, list) else data.get('data', [])
    
    # Get country mapping for foreign keys
    from sqlalchemy import select
    result = await session.execute(select(Country))
    countries = {c.country_code: c.id for c in result.scalars().all()}
    
    print(f"Importing {len(regions_list)} regions...")
    imported = 0
    
    for item in regions_list:
        country_code = item.get('country_code')
        country_id = countries.get(country_code)
        
        if not country_id:
            continue
        
        region = Region(
            id=str(item.get('id')),
            name=item.get('name'),
            country_id=country_id,
            latitude=item.get('latitude'),
            longitude=item.get('longitude')
        )
        session.add(region)
        imported += 1
    
    await session.commit()
    print(f"✓ Imported {imported} regions")


async def seed_cities(session: AsyncSession):
    """Import cities from CDN."""
    print("Fetching cities...")
    data = await fetch_json(f"{REMOTE_DATA_SOURCE_URL}/cities.json")
    
    cities_list = data if isinstance(data, list) else data.get('data', [])
    
    # Get region mapping
    from sqlalchemy import select
    result = await session.execute(select(Region))
    regions = {r.id: r.id for r in result.scalars().all()}
    
    print(f"Importing {len(cities_list)} cities (this may take a while)...")
    imported = 0
    batch_size = 1000
    batch = []
    
    for item in cities_list:
        state_id = str(item.get('state_id'))
        
        if state_id not in regions:
            continue
        
        city = City(
            id=str(item.get('id')),
            name=item.get('name'),
            region_id=state_id,
            latitude=item.get('latitude'),
            longitude=item.get('longitude')
        )
        batch.append(city)
        imported += 1
        
        # Commit in batches for performance
        if len(batch) >= batch_size:
            session.add_all(batch)
            await session.commit()
            print(f"  Imported {imported} cities so far...")
            batch = []
    
    # Final batch
    if batch:
        session.add_all(batch)
        await session.commit()
    
    print(f"✓ Imported {imported} cities")


async def main():
    """Run seeding process."""
    print("=== WorldTravel Data Seeding ===\n")
    
    if not settings.DATABASE_URL:
        print("Error: DATABASE_URL not configured")
        return
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await seed_countries(session)
            await seed_regions(session)
            await seed_cities(session)
            
            print("\n✓ All data imported successfully!")
            
        except Exception as e:
            print(f"\n✗ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
