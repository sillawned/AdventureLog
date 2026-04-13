# Docker Compose Setup Guide

This guide covers all aspects of running AdventureLog with Docker Compose, including development, production, and advanced configurations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Files](#configuration-files)
3. [Development Setup](#development-setup)
4. [Production Setup](#production-setup)
5. [Traefik Setup (with SSL/TLS)](#traefik-setup)
6. [Environment Variables](#environment-variables)
7. [Health Checks](#health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)
- 2GB+ available RAM
- 5GB+ free disk space

### 5-Minute Setup (Development)

```bash
# 1. Clone the repository
git clone https://github.com/seanmorley15/AdventureLog.git
cd AdventureLog

# 2. Create environment file
cp .env.example .env

# 3. Start services
docker-compose -f docker-compose.dev.yml up

# 4. Access the application
# Frontend: http://localhost:8015
# Backend API: http://localhost:8016
# Admin panel: http://localhost:8016/admin
```

Default credentials:
- Username: `admin`
- Password: `admin`

## Configuration Files

AdventureLog provides three main Docker Compose configurations:

### `docker-compose.yml` (Production)

Used for production deployments with pre-built images from GitHub Container Registry.

**Features:**
- Optimized production images
- Version-pinned containers
- Minimal logging
- All services have health checks

**Usage:**
```bash
docker-compose up -d
```

### `docker-compose.dev.yml` (Development)

Used for local development with services built from source code.

**Features:**
- Builds services from Dockerfile
- Hot-reload for frontend code changes
- Development logging
- All services have health checks
- Backend runs in development mode

**Usage:**
```bash
docker-compose -f docker-compose.dev.yml up
```

### `docker-compose-traefik.yaml` (Production with Reverse Proxy)

Advanced production setup with Traefik reverse proxy for SSL/TLS termination.

**Features:**
- Automatic SSL/TLS certificates via Let's Encrypt
- Virtual host routing
- Simplified port management
- Traefik dashboard for monitoring

**Usage:**
```bash
cp .env.traefik.example .env.traefik
# Edit .env.traefik with your domain and email
docker-compose -f docker-compose-traefik.yaml up -d
```

## Development Setup

### Initial Setup

1. **Clone and navigate to project:**
   ```bash
   git clone https://github.com/seanmorley15/AdventureLog.git
   cd AdventureLog
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Start development services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

   Wait for all services to be healthy (look for "healthy" status in logs)

4. **Access the application:**
   - Frontend: http://localhost:8015
   - Backend API: http://localhost:8016
   - Admin panel: http://localhost:8016/admin

### Development Workflow

**Making code changes:**

- **Frontend changes:** Automatically hot-reloaded on port 3000/8015
- **Backend changes:** Restart the backend service with `docker-compose -f docker-compose.dev.yml restart server`
- **Database changes:** Run migrations with `docker-compose -f docker-compose.dev.yml exec server python manage.py migrate`

**Running Django commands:**
```bash
docker-compose -f docker-compose.dev.yml exec server python manage.py <command>
```

**Accessing database:**
```bash
docker-compose -f docker-compose.dev.yml exec db psql -U adventurelog -d adventurelog
```

**Viewing logs:**
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f server
```

### Stopping Services

```bash
# Stop all services (containers remain)
docker-compose -f docker-compose.dev.yml stop

# Remove all containers
docker-compose -f docker-compose.dev.yml down

# Remove containers and volumes (WARNING: deletes data!)
docker-compose -f docker-compose.dev.yml down -v
```

## Production Setup

### Prerequisites

- Domain name (e.g., adventurelog.example.com)
- Server with Docker and Docker Compose installed
- Ports 80 and 443 accessible (for SSL)
- Minimum 2GB RAM, 10GB disk space

### Initial Deployment

1. **Prepare the server:**
   ```bash
   git clone https://github.com/seanmorley15/AdventureLog.git
   cd AdventureLog
   ```

2. **Create production environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Update environment variables in `.env`:**
   - Change `DEBUG=False` (already set in template)
   - Update `SECRET_KEY` with a unique secure value
   - Set `PUBLIC_URL` to your domain
   - Set strong passwords for database and admin user
   - Update `CSRF_TRUSTED_ORIGINS` with your domain

4. **Set image versions:**
   Update the image tags in `docker-compose.yml`:
   ```yaml
   image: ghcr.io/seanmorley15/adventurelog-frontend:v0.12.0
   image: ghcr.io/seanmorley15/adventurelog-backend:v0.12.0
   ```

5. **Start services:**
   ```bash
   docker-compose up -d
   ```

6. **Verify health:**
   ```bash
   docker-compose ps
   # All services should show "healthy" status
   ```

### Updating Production

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# View logs for any errors
docker-compose logs
```

### Backup and Recovery

**Backup database:**
```bash
docker-compose exec db pg_dump -U adventurelog adventurelog > backup.sql
```

**Backup media files:**
```bash
docker cp adventurelog-backend:/code/media ./media_backup
```

**Restore database:**
```bash
docker-compose exec -T db psql -U adventurelog adventurelog < backup.sql
```

## Traefik Setup

Traefik provides automatic SSL/TLS certificate management and reverse proxy capabilities.

### Prerequisites

- Domain name pointing to your server
- Ports 80 and 443 accessible from the internet
- Email for Let's Encrypt notifications

### Setup Instructions

1. **Prepare environment:**
   ```bash
   cp .env.traefik.example .env.traefik
   ```

2. **Edit `.env.traefik` with your values:**
   ```bash
   DOMAIN=adventurelog.example.com
   LETSENCRYPT_EMAIL=admin@example.com
   SECRET_KEY=<generate-a-secure-value>
   POSTGRES_PASSWORD=<use-a-strong-password>
   DJANGO_ADMIN_PASSWORD=<use-a-strong-password>
   ```

3. **Start Traefik setup:**
   ```bash
   docker-compose -f docker-compose-traefik.yaml up -d
   ```

4. **Monitor certificate generation:**
   ```bash
   docker-compose -f docker-compose-traefik.yaml logs traefik
   ```

5. **Access application:**
   - Web: https://adventurelog.example.com
   - Traefik Dashboard: http://localhost:8080

### Traefik Configuration

The Traefik compose file automatically:
- Routes requests to the correct service based on hostname and path
- Manages SSL/TLS certificates via Let's Encrypt
- Redirects HTTP to HTTPS
- Handles static files and media uploads

**Traefik routing rules:**
- Frontend: `Host(example.com) && !(PathPrefix(/media) || PathPrefix(/admin) ...)`
- Backend: `Host(example.com) && (PathPrefix(/media) || PathPrefix(/admin) ...)`

### Traefik Dashboard

Access at `http://your-server:8080` to monitor:
- Active routers and services
- Certificate status
- Request statistics

⚠️ **Important:** The dashboard is insecure. In production:
1. Disable the dashboard (`--api.insecure=false`)
2. Or protect it with authentication
3. Or remove the `--api.insecure=true` command entirely

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (must be unique!) | `django-insecure-...` |
| `POSTGRES_PASSWORD` | Database password | `SecurePassword123!` |
| `DJANGO_ADMIN_PASSWORD` | Admin user password | `AdminPassword123!` |

### Frontend Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PUBLIC_SERVER_URL` | `http://server:8000` | Backend API URL |
| `ORIGIN` | `http://localhost:8015` | Frontend origin (CORS) |
| `FRONTEND_PORT` | `8015` | Frontend port on host |
| `BODY_SIZE_LIMIT` | `Infinity` | Max request size |

### Database Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PGHOST` | `db` | Database host |
| `POSTGRES_DB` | `adventurelog` | Database name |
| `POSTGRES_USER` | `adventurelog` | Database user |
| `POSTGRES_PASSWORD` | `changeme123` | Database password (CHANGE THIS!) |

### Backend Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `False` | Django debug mode |
| `PUBLIC_URL` | `http://localhost:8016` | Public URL of application |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:*` | CSRF-allowed origins |
| `FRONTEND_URL` | `http://localhost:8015` | Frontend URL |
| `BACKEND_PORT` | `8016` | Backend port on host |

See `.env.example` for a complete list of variables including optional integrations.

## Health Checks

All services include health checks that verify they're working correctly.

### Health Check Status

```bash
docker-compose ps
```

Look for "healthy" status:
```
NAME                    STATUS
adventurelog-frontend   Up 2 minutes (healthy)
adventurelog-db         Up 2 minutes (healthy)
adventurelog-backend    Up 2 minutes (healthy)
```

### What Health Checks Do

- **Database:** Verifies PostgreSQL connectivity
- **Frontend:** Checks if Vite dev server (dev) or Node server (production) responds
- **Backend:** Checks if Django app and Nginx are running

### Manual Health Checks

```bash
# Frontend
curl http://localhost:8015/

# Backend
curl http://localhost:8016/health/

# Database
docker-compose exec db pg_isready -U adventurelog
```

### Troubleshooting Health Checks

If a service is unhealthy:
```bash
# View detailed logs
docker-compose logs <service-name>

# Inspect the service
docker-compose exec <service-name> /bin/bash
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port
lsof -i :8015  # Frontend
lsof -i :8016  # Backend

# Change ports in .env
FRONTEND_PORT=8020
BACKEND_PORT=8021
```

#### 2. Out of Memory

Frontend or backend crashing with exit code 137 (OOM):

**Option 1: Increase Docker memory limit**
- Docker Desktop: Preferences → Resources → Memory
- Linux: Use `docker-compose.override.yml` to limit services

**Option 2: Use override file**
```bash
cp docker-compose.override.yml.example docker-compose.override.yml
# Uncomment memory limits
docker-compose -f docker-compose.dev.yml up
```

#### 3. Database Won't Start

```bash
# Check logs
docker-compose logs db

# Remove and recreate database volume
docker-compose down -v
docker-compose up db
```

#### 4. Frontend Build Fails

```bash
# Clear pnpm cache
docker-compose -f docker-compose.dev.yml exec web rm -rf /pnpm-store
docker-compose -f docker-compose.dev.yml restart web

# Or restart from scratch
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up
```

#### 5. Backend Migrations Fail

```bash
# Check Django logs
docker-compose -f docker-compose.dev.yml logs server

# Run migrations manually
docker-compose -f docker-compose.dev.yml exec server python manage.py migrate --verbosity 3

# Rollback last migration if needed
docker-compose -f docker-compose.dev.yml exec server python manage.py migrate app_name 0001
```

### Useful Commands

```bash
# Validate compose files
docker-compose -f docker-compose.dev.yml config

# View all environment variables in a service
docker-compose -f docker-compose.dev.yml exec server env | sort

# Access database shell
docker-compose -f docker-compose.dev.yml exec db psql -U adventurelog

# Create Django superuser
docker-compose -f docker-compose.dev.yml exec server python manage.py createsuperuser

# Static file collection
docker-compose -f docker-compose.dev.yml exec server python manage.py collectstatic --noinput

# Run tests
docker-compose -f docker-compose.dev.yml exec server python manage.py test
```

## Advanced Configuration

### Using docker-compose.override.yml

Docker Compose automatically merges `docker-compose.override.yml` with your main configuration, allowing local customizations:

```bash
# Copy the example
cp docker-compose.override.yml.example docker-compose.override.yml

# Edit to customize memory limits, add pgAdmin, Mailhog, etc.
vim docker-compose.override.yml

# Services will use override settings automatically
docker-compose -f docker-compose.dev.yml up
```

### Resource Limits

Set CPU and memory limits to prevent one service from consuming all resources:

```yaml
services:
  server:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Custom Networks

By default, all services use the same network. Create custom networks:

```yaml
networks:
  frontend:
  backend:

services:
  web:
    networks:
      - frontend
  server:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend
```

### Using External Database

If you want to use an external PostgreSQL database:

1. Remove the `db` service from compose file
2. Set `PGHOST` to your database server
3. Ensure the database user and permissions are configured

### Scaling Services

To run multiple instances of a service:

```bash
# Run 3 backend instances with load balancing
docker-compose -f docker-compose.dev.yml up -d --scale server=3
```

Note: Load balancing requires additional configuration with a reverse proxy.

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Documentation](https://docs.djangoproject.com/)
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [Traefik Documentation](https://doc.traefik.io/)

## Support

For issues specific to AdventureLog Docker setup:
- Check the [main README](../README.md)
- Search [GitHub Issues](https://github.com/seanmorley15/AdventureLog/issues)
- Review [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
