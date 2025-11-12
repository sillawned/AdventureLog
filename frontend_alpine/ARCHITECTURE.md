# Frontend Modular Architecture

## Overview
The `app.js` file has been split into **11 modular files** for better maintainability and organization.

## File Structure

```
templates/scripts/
├── config.js          # API configuration (5 lines)
├── state.js           # Initial state definition (90 lines)
├── api.js             # API helper methods (43 lines)
├── auth.js            # Authentication methods (70 lines)
├── locations.js       # Location CRUD + sub-resources (305 lines)
├── collections.js     # Collections & categories (60 lines)
├── ui.js              # UI enhancements (geolocation, tags, validation, shortcuts) (185 lines)
├── filters.js         # Search, filter, pagination (115 lines)
├── map.js             # Leaflet map integration (55 lines)
├── stats.js           # Statistics and visits (10 lines)
└── app-modular.js     # Main app that combines all modules (38 lines)
```

## Module Descriptions

### 1. **config.js**
- API_URL constant
- Environment configuration

### 2. **state.js**
- `getInitialState()` function
- Returns all initial state properties
- Forms, data arrays, UI state, validation state

### 3. **api.js**
- `api()` - Main API fetch wrapper
- `showError()` - Error notifications
- `showSuccess()` - Success notifications

### 4. **auth.js**
- `login()` - User authentication
- `register()` - User registration
- `logout()` - Session cleanup
- `fetchUser()` - Get current user

### 5. **locations.js** (Largest module)
- Location CRUD operations
- Sub-resource management:
  - Notes (create, fetch, delete)
  - Activities (create, fetch, delete)
  - Checklists (create, fetch, delete, toggle items)
  - Transportation (create, fetch, delete)
  - Lodging (create, fetch, delete)
  - Trails (create, fetch, delete)

### 6. **collections.js**
- Collections CRUD
- Categories CRUD

### 7. **ui.js**
- `toggleTheme()` / `applyTheme()` - Dark mode
- `getCurrentLocation()` - Browser geolocation
- Tag suggestions (computed properties + methods)
- Address autocomplete with Nominatim
- Form validation logic
- `setupKeyboardShortcuts()` - Ctrl+N, Escape

### 8. **filters.js**
- `filteredLocations` (computed) - Search + filter + sort
- `filteredCollections` (computed) - Search collections
- `filteredCategories` (computed) - Search categories
- Pagination (computed properties + methods)

### 9. **map.js**
- `initMap()` - Initialize Leaflet
- `updateMapMarkers()` - Render markers with popups

### 10. **stats.js**
- `fetchStats()` - Dashboard statistics
- `fetchAllVisits()` - Visit history

### 11. **app-modular.js**
- Combines all modules using spread operator
- Defines lifecycle methods (`init()`)
- Merges computed properties and methods

## Benefits

✅ **Maintainability**: Easy to find and edit specific features
✅ **Readability**: Each file has a clear purpose
✅ **Smaller Files**: Largest module is ~305 lines (vs 1100 in monolithic)
✅ **Reusability**: Modules can be tested independently
✅ **Collaboration**: Multiple devs can work on different modules
✅ **Debugging**: Easier to trace issues to specific modules
✅ **Build Size**: Reduced from 114KB to 97KB (removed duplicates)

## How It Works

The `base.html` template includes all modules in order:

```html
<script>
    {% include 'scripts/config.js' %}
    {% include 'scripts/state.js' %}
    {% include 'scripts/api.js' %}
    {% include 'scripts/auth.js' %}
    {% include 'scripts/locations.js' %}
    {% include 'scripts/collections.js' %}
    {% include 'scripts/ui.js' %}
    {% include 'scripts/filters.js' %}
    {% include 'scripts/map.js' %}
    {% include 'scripts/stats.js' %}
    {% include 'scripts/app-modular.js' %}
</script>
```

All modules are combined at build time by Jinja2, resulting in a single optimized HTML file.

## Adding New Features

**Example: Adding a new feature to locations**

1. Open `locations.js`
2. Add your method to the `locationMethods` object:
   ```javascript
   async myNewFeature() {
       // your code
   }
   ```
3. The method is automatically available in Alpine.js via `app-modular.js`
4. No changes needed to other modules!

## Computed Properties

Computed properties (using `get`) must be defined in the main app object. They're included from:
- `filterMethods` (filteredLocations, pagination)
- `uiMethods` (tag suggestions)

## Notes

- The original `app.js` is still present but no longer used
- All functionality is preserved
- No breaking changes to the UI
- Same Alpine.js API surface
