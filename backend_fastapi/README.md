# AdventureLog FastAPI Backend

Clean, modern FastAPI implementation with SQLAlchemy ORM and JWT authentication.

## Architecture

```
app/
├── routers/              # API endpoints (simplified structure)
│   ├── auth.py          # Registration, login, JWT tokens
│   ├── locations.py     # Locations CRUD
│   ├── collections.py   # Collections CRUD
│   └── visits.py        # Visits CRUD
├── models/              # SQLAlchemy ORM models
│   ├── user.py         # User model
│   ├── adventure.py    # Location, Visit, Collection, etc.
│   └── base.py         # Database session management
├── crud/                # Database operations
│   ├── user.py         # User CRUD operations
│   └── adventure.py    # Adventure domain CRUD
├── core/                # Core utilities
│   ├── config.py       # Settings management
│   └── security.py     # JWT + bcrypt password hashing
├── deps.py             # FastAPI dependencies (auth, etc.)
└── main.py             # Application entry point
```

## Features

- ✅ **JWT Authentication**: Secure token-based auth with bcrypt
- ✅ **SQLAlchemy 2.0**: Async ORM with proper relationships
- ✅ **UUID Primary Keys**: For locations, visits, collections
- ✅ **Full CRUD APIs**: 13 routers covering all domain models
- ✅ **Ownership Validation**: Users can only edit their own data
- ✅ **Public Sharing**: Optional public flag for locations/collections

## Quick Start

### Using Docker (Recommended)

```bash
cd /home/user/workspace/AdventureLog
docker compose -f docker-compose.test.yml up
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: PostgreSQL on port 5432

### Local Development

1. Install dependencies:
```bash
cd backend_fastapi
pip install -e .
```

2. Set environment variables:
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/adventurelog"
export SECRET_KEY="your-secret-key"
```

3. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/token` - Login (OAuth2 password flow)
- `GET /api/auth/me` - Get current user

### Locations
- `GET /api/locations/` - List user's locations
- `GET /api/locations/public` - List public locations
- `POST /api/locations/` - Create location
- `GET /api/locations/{id}` - Get location details
- `PUT /api/locations/{id}` - Update location
- `DELETE /api/locations/{id}` - Delete location

### Collections
- `GET /api/collections/` - List user's collections
- `POST /api/collections/` - Create collection
- `GET /api/collections/{id}` - Get collection details
- `PUT /api/collections/{id}` - Update collection
- `DELETE /api/collections/{id}` - Delete collection

### Visits
- `POST /api/visits/` - Create visit
- `GET /api/visits/{id}` - Get visit details
- `PATCH /api/visits/{id}` - Update visit
- `DELETE /api/visits/{id}` - Delete visit

## Database Models

### Location
- UUID id, user_id, name, city, country, address
- latitude, longitude (coordinates)
- rating (1-5), tags (array), is_public
- created_at, updated_at

### Collection
- UUID id, user_id, name
- is_public, is_archived
- created_at, updated_at

### Visit
- UUID id, location_id
- start_date, end_date
- created_at, updated_at

## Development Notes

- **Simplified Structure**: Routers in `app/routers/`, models in `app/models/`
- **Inline Schemas**: Pydantic models defined in routers alongside endpoints
- **bcrypt Passwords**: Direct bcrypt implementation for password hashing
- **Clean Tables**: Simple table names (locations, visits, users, collections, etc.)

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=pass123"

# Create location (use token from login)
curl -X POST http://localhost:8000/api/locations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Paris","city":"Paris","country":"France","rating":5}'
```
