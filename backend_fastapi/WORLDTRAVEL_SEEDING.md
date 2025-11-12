# WorldTravel Data Seeding

## Overview

The WorldTravel feature requires reference data for countries, regions (states/provinces), and cities. This data is seeded from the [dr5hn/countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) dataset, hosted on the AdventureLog CDN.

## Seeding Command

To populate the worldtravel tables, run:

```bash
cd /home/user/workspace/AdventureLog/backend_fastapi
python -m app.scripts.seed_worldtravel
```

This will:
1. Fetch countries, regions, and cities from the CDN
2. Import them into the database
3. Create proper relationships between entities

## Data Structure

- **Countries** (~250): ISO2 code, name, capital, coordinates
- **Regions** (~5,000): States/provinces linked to countries
- **Cities** (~150,000+): Cities linked to regions

## Requirements

- Database must be initialized (tables created)
- `httpx` dependency installed (already in pyproject.toml)
- Network access to `https://cdn.adventurelog.app/data/`

## Troubleshooting

If the CDN is unavailable, you can:
1. Download the JSON files manually from the repository
2. Modify `CDN_BASE_URL` in `seed_worldtravel.py` to point to local files
3. Use environment variable to override the CDN URL

## Performance Notes

- Countries: ~1 second
- Regions: ~5 seconds
- Cities: 2-5 minutes (batch inserts used)

Total seeding time: ~5 minutes
