# Docker Testing Guide for AdventureLog

## Quick Start

### Development Mode (Default)
Run both frontend and backend in development mode with hot reload:

```bash
# Start all services
docker-compose -f docker-compose.test.yml up

# Or start in detached mode
docker-compose -f docker-compose.test.yml up -d

# View logs
docker-compose -f docker-compose.test.yml logs -f

# Stop services
docker-compose -f docker-compose.test.yml down
```

Access:
- **Frontend (Astro)**: http://localhost:4321
- **Backend (FastAPI)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### Production Mode
Test production builds:

```bash
# Build and start production services
docker-compose -f docker-compose.test.yml --profile production up

# Or build separately
docker-compose -f docker-compose.test.yml --profile production build
docker-compose -f docker-compose.test.yml --profile production up
```

Access:
- **Frontend (Production)**: http://localhost:4322
- **Backend (Production)**: http://localhost:8001

## Individual Service Testing

### Test Backend Only
```bash
# Start database
docker-compose -f docker-compose.test.yml up postgres -d

# Start backend in development
docker-compose -f docker-compose.test.yml up backend-dev

# Or build and run standalone
cd backend_fastapi
docker build -f Dockerfile.new --target development -t adventurelog-backend:dev .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://adventurelog:adventurelog_password@host.docker.internal:5432/adventurelog \
  adventurelog-backend:dev
```

### Test Frontend Only
```bash
# Assuming backend is running on localhost:8000
cd frontend_astro
docker build -f Dockerfile.new --target development -t adventurelog-frontend:dev .
docker run -p 4321:4321 \
  -e PUBLIC_API_URL=http://localhost:8000 \
  -v $(pwd)/src:/app/src:ro \
  adventurelog-frontend:dev
```

## Build Stages

### Backend Stages
- **base**: Python 3.11 with system dependencies
- **development**: Includes hot reload, development dependencies
- **production**: Optimized with multiple workers, non-root user

### Frontend Stages
- **deps**: Install node dependencies
- **builder**: Build production assets
- **development**: Run dev server with hot reload
- **production**: Serve built static files

## Environment Variables

### Backend Environment Variables
Create a `.env` file in the project root:

```env
# Database
POSTGRES_DB=adventurelog
POSTGRES_USER=adventurelog
POSTGRES_PASSWORD=adventurelog_password

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs (optional)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### Frontend Environment Variables
```env
PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Common Commands

### Rebuild Services
```bash
# Rebuild all services
docker-compose -f docker-compose.test.yml build

# Rebuild specific service
docker-compose -f docker-compose.test.yml build backend-dev
docker-compose -f docker-compose.test.yml build frontend-dev

# Rebuild without cache
docker-compose -f docker-compose.test.yml build --no-cache
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.test.yml logs -f

# Specific service
docker-compose -f docker-compose.test.yml logs -f backend-dev
docker-compose -f docker-compose.test.yml logs -f frontend-dev

# Last 100 lines
docker-compose -f docker-compose.test.yml logs --tail=100
```

### Execute Commands Inside Containers
```bash
# Backend shell
docker-compose -f docker-compose.test.yml exec backend-dev sh

# Frontend shell
docker-compose -f docker-compose.test.yml exec frontend-dev sh

# Run database migrations (example)
docker-compose -f docker-compose.test.yml exec backend-dev python -m alembic upgrade head

# Install new npm package
docker-compose -f docker-compose.test.yml exec frontend-dev npm install package-name
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.test.yml exec postgres psql -U adventurelog -d adventurelog

# Backup database
docker-compose -f docker-compose.test.yml exec postgres pg_dump -U adventurelog adventurelog > backup.sql

# Restore database
docker-compose -f docker-compose.test.yml exec -T postgres psql -U adventurelog adventurelog < backup.sql
```

## Troubleshooting

### Container Won't Start
```bash
# Check container status
docker-compose -f docker-compose.test.yml ps

# Check logs for errors
docker-compose -f docker-compose.test.yml logs backend-dev

# Remove containers and volumes
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :4321

# Or change ports in docker-compose.test.yml
```

### Frontend Can't Connect to Backend
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Check PUBLIC_API_URL environment variable
3. Check network connectivity: `docker-compose -f docker-compose.test.yml exec frontend-dev ping backend-dev`

### Database Connection Issues
```bash
# Check if database is healthy
docker-compose -f docker-compose.test.yml ps postgres

# Test connection from backend
docker-compose -f docker-compose.test.yml exec backend-dev psql postgresql://adventurelog:adventurelog_password@postgres:5432/adventurelog
```

### Hot Reload Not Working
- Ensure volume mounts are correct in docker-compose.test.yml
- On Windows/Mac, check Docker Desktop file sharing settings
- Try rebuilding: `docker-compose -f docker-compose.test.yml up --build`

## Performance Tips

### Speed Up Builds
1. Use `.dockerignore` files to exclude unnecessary files
2. Order Dockerfile commands from least to most frequently changing
3. Use BuildKit: `DOCKER_BUILDKIT=1 docker-compose -f docker-compose.test.yml build`

### Reduce Image Size
- Production images use multi-stage builds to exclude dev dependencies
- Alpine base images for smaller footprint
- .dockerignore excludes node_modules, __pycache__, etc.

## Clean Up

```bash
# Stop and remove containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (WARNING: deletes database data)
docker-compose -f docker-compose.test.yml down -v

# Remove images
docker-compose -f docker-compose.test.yml down --rmi all

# Full cleanup (containers, volumes, images, networks)
docker-compose -f docker-compose.test.yml down -v --rmi all
docker system prune -a
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Test with Docker

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build images
        run: docker-compose -f docker-compose.test.yml build
      
      - name: Start services
        run: docker-compose -f docker-compose.test.yml up -d
      
      - name: Wait for services
        run: |
          sleep 10
          curl --retry 10 --retry-delay 5 http://localhost:8000/health
      
      - name: Run tests
        run: docker-compose -f docker-compose.test.yml exec -T backend-dev pytest
      
      - name: Stop services
        run: docker-compose -f docker-compose.test.yml down
```

## Next Steps

1. **Run Development Environment**:
   ```bash
   docker-compose -f docker-compose.test.yml up
   ```

2. **Test the Application**:
   - Open http://localhost:4321 in your browser
   - Create an account via /signup
   - Test API at http://localhost:8000/docs

3. **Make Changes**:
   - Edit files in `frontend_astro/src/` or `backend_fastapi/app/`
   - Changes will hot reload automatically

4. **Test Production Build**:
   ```bash
   docker-compose -f docker-compose.test.yml --profile production up
   ```
