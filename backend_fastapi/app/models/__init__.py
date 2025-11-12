"""SQLAlchemy models package."""
from .base import Base, get_db, init_db, create_tables, close_db
from .user import User
from .adventure import (
    Location,
    Visit,
    Collection,
    Category,
    Transportation,
    Note,
    Checklist,
    ChecklistItem,
    Activity,
    Lodging,
    Trail,
)
from .worldtravel import (
    Country,
    Region,
    City,
    VisitedRegion,
    VisitedCity,
)
from .integrations import (
    ImmichIntegration,
    StravaToken,
    WandererIntegration,
)

__all__ = [
    "Base",
    "get_db",
    "init_db",
    "create_tables",
    "close_db",
    "User",
    "Location",
    "Visit",
    "Collection",
    "Category",
    "Transportation",
    "Note",
    "Checklist",
    "ChecklistItem",
    "Activity",
    "Lodging",
    "Trail",
    "Country",
    "Region",
    "City",
    "VisitedRegion",
    "VisitedCity",
    "ImmichIntegration",
    "StravaToken",
    "WandererIntegration",
]
