# Docker Image Size Analysis for FastAPI Backend

## Problem Statement
UV auto-selects Python 3.14 on Alpine, which requires compiling greenlet and SQLAlchemy from source (no musl wheels available yet).

## Solution: Multi-stage Build Patterns

### Pattern 1: Alpine + Python 3.12 + Direct venv (RECOMMENDED)
```dockerfile
Builder: Alpine + Python 3.12 + UV + build-tools
Runtime: Alpine + Python 3.12 + venv (NO UV, NO build-tools)
Command: uvicorn (from venv) directly
```

**Estimated Size:** ~85-110 MB
- Alpine base: ~8 MB
- Python 3.12: ~40 MB
- FastAPI + dependencies: ~35-60 MB

**Pros:**
✓ Smallest possible size
✓ Python 3.12 has good wheel coverage for musl
✓ No UV overhead at runtime
✓ No build tools in final image
✓ Fast startup (direct Python execution)

**Cons:**
✗ Some packages may still compile in builder stage
✗ Slightly more complex than pure Debian

---

### Pattern 2: Debian Slim + Python 3.12 + Direct venv
```dockerfile
Builder: Debian slim + Python 3.12 + UV + gcc
Runtime: Debian slim + Python 3.12 + venv (NO UV)
Command: uvicorn directly
```

**Estimated Size:** ~180-220 MB
- Debian slim base: ~80 MB
- Python 3.12: ~50 MB
- FastAPI + dependencies: ~50-90 MB

**Pros:**
✓ Almost all wheels pre-built (glibc compatibility)
✓ Very stable and predictable
✓ No compilation needed in most cases
✓ No UV at runtime

**Cons:**
✗ 2x larger than Alpine
✗ Debian includes more libs by default

---

### Pattern 3: Alpine + Python 3.14 + UV (CURRENT - PROBLEMATIC)
```dockerfile
Runtime: Alpine + Python 3.14 + UV + build-tools
Command: uv run server.py
```

**Estimated Size:** ~200-250 MB
- Alpine base: ~8 MB
- Python 3.14: ~45 MB
- UV binary: ~20 MB
- Build tools (gcc, musl-dev): ~80 MB
- Compiled packages: ~50-100 MB

**Pros:**
✓ Latest Python version

**Cons:**
✗ Largest option due to build tools
✗ Requires compilation at build time
✗ UV overhead on every startup
✗ Build tools in production image

---

## Size Comparison

| Pattern | Base | Python | Deps | Tools | Total |
|---------|------|--------|------|-------|-------|
| **Alpine 3.12 + venv** | 8 MB | 40 MB | 40 MB | 0 MB | **~88 MB** |
| Debian + venv | 80 MB | 50 MB | 50 MB | 0 MB | ~180 MB |
| Alpine 3.14 + UV | 8 MB | 45 MB | 60 MB | 100 MB | ~213 MB |

## Recommendation

**Use Alpine + Python 3.12 + Direct venv** (Pattern 1)

### Why Python 3.12?
- Most packages now have pre-built wheels for Python 3.12 + musl
- Stable and well-tested
- Avoids Python 3.14 bleeding-edge issues
- Still modern (type hints, performance improvements)

### Why No UV at Runtime?
- UV adds ~15-20 MB to image
- UV does sync checks on startup (slower)
- Direct Python execution is faster
- UV is great for dev, but unnecessary overhead in production

### The Builder Pattern
1. **Builder stage**: Use UV to install everything (with build tools)
2. **Runtime stage**: Copy only the `.venv` folder (pre-compiled)
3. **Runtime**: Execute Python directly from venv (no UV needed)

## Migration Path

Current:
```bash
uv run --no-sync app/server.py
```

Optimized:
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

Since `/app/.venv/bin` is in PATH, `uvicorn` command finds the venv-installed uvicorn directly.

## Testing Commands

```bash
# Build dev target
docker build -t adventurelog-backend:dev --target dev .

# Build production target
docker build -t adventurelog-backend:prod --target server .

# Check size
docker images adventurelog-backend

# Run dev
docker run -p 8000:8000 adventurelog-backend:dev

# Run production
docker run -p 8000:8000 adventurelog-backend:prod
```

## Expected Results

- Build time: ~2-3 minutes (first build, then cached)
- Runtime image: ~85-110 MB
- Startup time: ~1-2 seconds (vs ~3-5 with UV)
- No compilation errors from missing wheels
