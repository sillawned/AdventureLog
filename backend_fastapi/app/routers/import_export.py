"""Import/Export functionality for user data."""

import json
from typing import Dict, Any, List
from datetime import date, datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.base import get_db
from app.models.user import User
from app.deps import get_current_user
from app.crud.adventure import (
    get_user_locations,
    get_user_collections,
    get_user_categories,
    create_location,
    create_collection,
    create_category,
    create_visit,
)

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class ExportData(BaseModel):
    """Full user data export schema."""
    version: str = "2.0"
    exported_at: datetime
    user: Dict[str, Any]
    locations: List[Dict[str, Any]]
    collections: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]
    visits: List[Dict[str, Any]]


class ImportStats(BaseModel):
    """Import statistics."""
    locations_imported: int
    collections_imported: int
    categories_imported: int
    visits_imported: int
    errors: List[str]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def serialize_model(obj: Any) -> Dict[str, Any]:
    """Serialize SQLAlchemy model to dict."""
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        
        # Handle special types
        if isinstance(value, (datetime, date)):
            result[column.name] = value.isoformat()
        elif isinstance(value, UUID):
            result[column.name] = str(value)
        elif value is None:
            result[column.name] = None
        else:
            result[column.name] = value
    
    return result


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/export/json")
async def export_json(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user data as JSON."""
    # Fetch user data
    locations = await get_user_locations(db, current_user.id)
    collections = await get_user_collections(db, current_user.id)
    categories = await get_user_categories(db, current_user.id)
    
    # Fetch visits for all locations
    visits = []
    for location in locations:
        for visit in location.visits:
            visits.append(serialize_model(visit))
    
    # Build export data
    export_data = {
        "version": "2.0",
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
        },
        "locations": [serialize_model(loc) for loc in locations],
        "collections": [serialize_model(col) for col in collections],
        "categories": [serialize_model(cat) for cat in categories],
        "visits": visits,
    }
    
    # Return as downloadable JSON
    json_str = json.dumps(export_data, indent=2)
    
    return Response(
        content=json_str,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=adventurelog_export_{datetime.utcnow().strftime('%Y%m%d')}.json"
        }
    )


# ============================================================================
# IMPORT ENDPOINTS
# ============================================================================

@router.post("/import/json", response_model=ImportStats)
async def import_json(
    data: ExportData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Import user data from JSON export."""
    stats = {
        "locations_imported": 0,
        "collections_imported": 0,
        "categories_imported": 0,
        "visits_imported": 0,
        "errors": []
    }
    
    # Track ID mappings (old ID -> new ID)
    category_map = {}
    collection_map = {}
    location_map = {}
    
    try:
        # Import categories first
        for cat_data in data.categories:
            try:
                old_id = cat_data.get("id")
                category = await create_category(
                    db=db,
                    user_id=current_user.id,
                    name=cat_data["name"],
                    icon=cat_data.get("icon"),
                    color=cat_data.get("color"),
                )
                await db.flush()
                category_map[old_id] = category.id
                stats["categories_imported"] += 1
            except Exception as e:
                stats["errors"].append(f"Category import error: {str(e)}")
        
        # Import collections
        for col_data in data.collections:
            try:
                old_id = col_data.get("id")
                collection = await create_collection(
                    db=db,
                    collection_id=uuid4(),
                    user_id=current_user.id,
                    name=col_data["name"],
                    description=col_data.get("description"),
                    start_date=col_data.get("start_date"),
                    end_date=col_data.get("end_date"),
                    link=col_data.get("link"),
                    is_public=col_data.get("is_public", False),
                )
                await db.flush()
                collection_map[old_id] = collection.id
                stats["collections_imported"] += 1
            except Exception as e:
                stats["errors"].append(f"Collection import error: {str(e)}")
        
        # Import locations
        for loc_data in data.locations:
            try:
                old_id = loc_data.get("id")
                old_category_id = loc_data.get("category_id")
                old_collection_id = loc_data.get("collection_id")
                
                # Map old IDs to new IDs
                new_category_id = category_map.get(old_category_id) if old_category_id else None
                new_collection_id = collection_map.get(old_collection_id) if old_collection_id else None
                
                location = await create_location(
                    db=db,
                    location_id=uuid4(),
                    user_id=current_user.id,
                    name=loc_data["name"],
                    description=loc_data.get("description"),
                    latitude=loc_data.get("latitude"),
                    longitude=loc_data.get("longitude"),
                    address=loc_data.get("address"),
                    city=loc_data.get("city"),
                    state=loc_data.get("state"),
                    country=loc_data.get("country"),
                    rating=loc_data.get("rating"),
                    tags=loc_data.get("tags"),
                    link=loc_data.get("link"),
                    is_public=loc_data.get("is_public", False),
                    category_id=new_category_id,
                    collection_id=new_collection_id,
                )
                await db.flush()
                location_map[old_id] = location.id
                stats["locations_imported"] += 1
            except Exception as e:
                stats["errors"].append(f"Location import error: {str(e)}")
        
        # Import visits
        for visit_data in data.visits:
            try:
                old_location_id = visit_data.get("location_id")
                new_location_id = location_map.get(old_location_id)
                
                if new_location_id:
                    await create_visit(
                        db=db,
                        visit_id=uuid4(),
                        location_id=new_location_id,
                        start_date=visit_data.get("start_date"),
                        end_date=visit_data.get("end_date"),
                        timezone=visit_data.get("timezone"),
                        notes=visit_data.get("notes"),
                    )
                    await db.flush()
                    stats["visits_imported"] += 1
                else:
                    stats["errors"].append("Visit skipped: location not found")
            except Exception as e:
                stats["errors"].append(f"Visit import error: {str(e)}")
        
        # Commit all changes
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
    
    return ImportStats(**stats)
