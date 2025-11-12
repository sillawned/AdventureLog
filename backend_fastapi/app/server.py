"""AdventureLog FastAPI Application.

Clean, modern implementation with JWT authentication and SQLAlchemy ORM.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth, visits, locations, collections, notes, categories, stats,
    transportation, checklists, activities, lodging, trails, worldtravel, integrations, import_export
)
from app.models.base import init_db, create_tables, close_db
from app.core.config import settings

# Import models to register them with SQLAlchemy
from app.models import (
    User, Location, Visit, Collection, Country, Region, City,
    ImmichIntegration, StravaToken, WandererIntegration
)

app = FastAPI(
    title="AdventureLog",
    description="Track your adventures and travels",
    version="2.0.0"
)

# Configure CORS - in production, use specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


# API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(locations.router, prefix="/api/locations", tags=["Locations"])
app.include_router(collections.router, prefix="/api/collections", tags=["Collections"])
app.include_router(visits.router, prefix="/api/visits", tags=["Visits"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(transportation.router, prefix="/api/transportation", tags=["Transportation"])
app.include_router(checklists.router, prefix="/api/checklists", tags=["Checklists"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(lodging.router, prefix="/api/lodging", tags=["Lodging"])
app.include_router(trails.router, prefix="/api/trails", tags=["Trails"])
app.include_router(worldtravel.router, prefix="/api/worldtravel", tags=["WorldTravel"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(import_export.router, prefix="/api/data", tags=["Import/Export"])


@app.on_event("startup")
async def on_startup():
    """Initialize database on startup."""
    if settings.DATABASE_URL:
        init_db(settings.DATABASE_URL)
        try:
            await create_tables()
            print("✓ Database tables created successfully")
        except Exception as e:
            print(f"Note: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    """Clean up database connections on shutdown."""
    await close_db()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        server_header=False,
    )