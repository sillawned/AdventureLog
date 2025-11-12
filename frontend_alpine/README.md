# AdventureLog Frontend - Jinja2 Build System

## Overview

The frontend uses a **Jinja2-based build system** to maintain clean, modular code during development while producing an optimized single-file application for deployment.

## Project Structure

```
frontend_alpine/
├── build.py                    # Build script with watch mode
├── requirements.txt            # Python dependencies (jinja2, watchdog)
├── Dockerfile                  # Multi-stage build with Python + Nginx
├── templates/                  # Source files (edit these!)
│   ├── base.html              # Main template
│   ├── components/            # View components
│   │   ├── header.html
│   │   ├── alerts.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── locations.html
│   │   ├── location-detail.html
│   │   └── collections.html
│   ├── styles/                # CSS files
│   │   ├── variables.css
│   │   ├── base.css
│   │   └── components.css
│   └── scripts/               # JavaScript
│       └── app.js
├── dist/                       # Generated output (don't edit!)
│   └── index.html             # Built single-file app
└── index.html                  # Symlink/copy of dist/index.html for local testing
```

## Development Workflow

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Build Once

```bash
python build.py
```

Output: `dist/index.html` (63KB single file)

### 3. Watch Mode (Auto-rebuild)

```bash
python build.py --watch
```

This watches `templates/` for changes and rebuilds automatically.

### 4. Deploy

```bash
# Build Docker image (automatically runs build.py)
docker compose -f ../docker-compose.test.yml build frontend-alpine

# Start container
docker compose -f ../docker-compose.test.yml up frontend-alpine -d
```

## Making Changes

### Add a New View Component

1. Create `templates/components/my-view.html`
2. Include it in `templates/base.html`
3. Rebuild: `python build.py`

### Modify Styles

Edit files in `templates/styles/`

### Modify JavaScript

Edit `templates/scripts/app.js`

## Advantages

- ✅ ~30 focused files instead of 1200+ line monolith
- ✅ Clean git diffs and easy navigation
- ✅ Team-friendly development
- ✅ Same deployment (single file!)
- ✅ No runtime overhead

## Performance

- Build time: ~0.3s
- Output: ~63KB
- Docker: ~8MB
