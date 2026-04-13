# Frontend Alpine API Alignment Audit

## ✅ Properly Aligned Endpoints

### Authentication (`auth.js`)
- ✅ `POST /auth/token` - Login with OAuth2 form data
- ✅ `POST /auth/register/` - User registration (has trailing slash, backend doesn't require it)
- ✅ `GET /auth/me` - Get current user
- ⚠️ Missing: `POST /auth/logout` endpoint call (just clearing local storage)

### Locations (`locations.js`)
- ✅ `GET /locations/` - List locations with pagination
- ✅ `POST /locations/` - Create location
- ✅ `PUT /locations/{location_id}` - Update location
- ✅ `DELETE /locations/{location_id}` - Delete location
- ✅ `GET /locations/{location_id}` - Get single location (used in collections.js)

### Collections (`collections.js`)
- ✅ `GET /collections/` - List collections
- ✅ `POST /collections/` - Create collection
- ✅ `DELETE /collections/{collection_id}` - Delete collection
- ❌ Missing: `GET /collections/{collection_id}` - Not using single collection endpoint
- ❌ Missing: `PUT /collections/{collection_id}` - No update functionality

### Categories (`collections.js`)
- ✅ `GET /categories/` - List categories
- ✅ `POST /categories/` - Create category
- ✅ `DELETE /categories/{id}` - Delete category
- ❌ Missing: `PUT /categories/{category_id}` - No update functionality

### Stats (`stats.js`)
- ✅ `GET /stats/` - Get user statistics

### Visits (`stats.js` and `locations.js`)
- ✅ `GET /visits/` - List all visits (stats.js)
- ✅ `GET /visits/?location_id={location_id}` - Filter by location (locations.js)
- ✅ `POST /visits/` - Create visit
- ✅ `DELETE /visits/{visit_id}` - Delete visit
- ❌ Missing: `GET /visits/{visit_id}` - Get single visit
- ❌ Missing: `PATCH /visits/{visit_id}` - Update visit

### Notes (`locations.js`)
- ✅ `GET /notes/location/{location_id}` - Get notes for location
- ✅ `POST /notes/` - Create note
- ✅ `DELETE /notes/{note_id}` - Delete note
- ❌ Missing: Update note functionality

### Activities (`locations.js`)
- ✅ `GET /activities/location/{location_id}` - Get activities for location
- ✅ `POST /activities/` - Create activity
- ✅ `DELETE /activities/{activity_id}` - Delete activity
- ❌ Missing: `PUT /activities/{activity_id}` - Update activity

### Checklists (`locations.js`)
- ✅ `GET /checklists/location/{location_id}` - Get checklists for location
- ✅ `POST /checklists/` - Create checklist
- ✅ `DELETE /checklists/{checklist_id}` - Delete checklist
- ✅ `POST /checklists/{checklist_id}/items` - Add checklist item
- ✅ `PUT /checklists/items/{item_id}` - Update checklist item (toggle checked)
- ✅ `DELETE /checklists/items/{item_id}` - Delete checklist item
- ❌ Missing: `PUT /checklists/{checklist_id}` - Update checklist

### Transportation (`locations.js`)
- ✅ `GET /transportation/location/{location_id}` - Get transportation for location
- ✅ `POST /transportation/` - Create transportation
- ✅ `DELETE /transportation/{transportation_id}` - Delete transportation
- ❌ Missing: `PUT /transportation/{transportation_id}` - Update transportation

### Lodging (`locations.js`)
- ✅ `GET /lodging/location/{location_id}` - Get lodging for location
- ✅ `POST /lodging/` - Create lodging
- ✅ `DELETE /lodging/{lodging_id}` - Delete lodging
- ❌ Missing: `PUT /lodging/{lodging_id}` - Update lodging

### Trails (`locations.js`)
- ✅ `GET /trails/location/{location_id}` - Get trails for location
- ✅ `POST /trails/` - Create trail
- ✅ `DELETE /trails/{trail_id}` - Delete trail
- ❌ Missing: `PUT /trails/{trail_id}` - Update trail

### World Travel (`worldtravel.js`)
- ✅ `GET /worldtravel/countries/` - Get all countries
- ✅ `GET /worldtravel/countries/{country_code}/regions/` - Get regions in country
- ✅ `GET /worldtravel/countries/{country_code}/visits/` - Get visited regions in country
- ✅ `GET /worldtravel/regions/{region_id}/cities/` - Get cities in region
- ✅ `GET /worldtravel/regions/{region_id}/visits/` - Get visited cities in region
- ✅ `GET /worldtravel/visited-regions/` - Get all visited regions
- ✅ `POST /worldtravel/visited-regions/` - Mark region as visited
- ✅ `DELETE /worldtravel/visited-regions/{region_id}` - Unmark region
- ✅ `GET /worldtravel/visited-cities/` - Get all visited cities
- ✅ `POST /worldtravel/visited-cities/` - Mark city as visited
- ✅ `DELETE /worldtravel/visited-cities/{city_id}` - Unmark city

## ❌ Missing Features

### High Priority
1. **Edit functionality for most entities** - Only locations have full CRUD, everything else is create/delete only
2. **Integrations** - No UI for Immich, Strava, or Wanderer integrations
3. **Import/Export** - No UI for JSON import/export
4. **Visit updates** - Can't edit visits after creation
5. **Collection updates** - Can't edit collection details

### Medium Priority
6. **Note updates** - Can't edit notes
7. **Activity updates** - Can't edit activities
8. **Trail updates** - Can't edit trails
9. **Transportation updates** - Can't edit transportation
10. **Lodging updates** - Can't edit lodging

### Low Priority
11. **Public location viewing** - No public endpoints being used
12. **Location images** - No image upload/management UI
13. **Profile viewing** - No user profile pages

## 🔧 Issues to Fix

### Authentication
- Should call `POST /auth/logout` endpoint instead of just clearing local storage
- Register endpoint has inconsistent trailing slash (backend accepts both)

### Collections
- `viewCollection` just filters local data instead of fetching from API
- Missing update functionality

### Error Handling
- API responses are inconsistent (some return arrays, some return objects with arrays)
- Need better error message parsing for validation errors

## ⚠️ Non-Functional Code (Backend Endpoints Don't Exist)

### additional-features.js - Dead Code
The following features in `additional-features.js` call endpoints that don't exist in the FastAPI backend:

1. **Search** - `/search/` endpoint doesn't exist
2. **Calendar** - `/adventures/calendar/` and `/adventures/calendar/download/` don't exist
3. **Profile Updates** - `PATCH /auth/user/` doesn't exist
4. **Export** - `/export/` doesn't exist (should be `/import-export/export/json`)
5. **Account Deletion** - `DELETE /auth/user/` doesn't exist
6. **User Profiles** - `/users/{userId}/`, `/users/{userId}/stats/`, `/users/{userId}/locations/`, `/users/{userId}/collections/` don't exist

### Recommendation
- Remove or comment out non-functional code in `additional-features.js`
- Update export to use correct endpoint: `GET /import-export/export/json`
- Calendar, Search, and Profile features need backend implementation first

## 📋 Code Cleanup Needed

### ✅ Files Removed
- `app-modular.js.backup` - Deleted

### ⚠️ Files with Dead Code
- **`additional-features.js`** - Contains many non-functional features (search, calendar, user profiles, etc.)
  - Only working feature: Export (but uses wrong endpoint `/export/` instead of `/import-export/export/json`)
  - Recommend: Comment out non-functional code or remove entirely

### 📁 File Organization
- **`map.js`** - Simple map with basic markers for locations list view
- **`map-view.js`** - Enhanced map with visit status, category icons, filters - Used for dedicated map view
- Both are needed but serve different purposes

### 🔍 Files to Review
- `ui.js` - Verify all UI helpers are being used
- Check if all component HTML templates are referenced in routing

## 🎨 Svelte Components from Main Frontend Worth Porting

### High Value Components
1. **MarkdownEditor.svelte** - Rich text editing for notes/descriptions
2. **ImageDropdown.svelte** / **ImageDisplayModal.svelte** - Image management
3. **ShareModal.svelte** - Collection sharing UI
4. **TimezoneSelector.svelte** - Better timezone selection
5. **TagComplete.svelte** - Tag autocomplete functionality
6. **MapStyleSelector.svelte** - Allow users to change map styles
7. **DateRangeCollapse.svelte** - Better date range UI

### Medium Value Components
8. **ChecklistModal.svelte** - Full checklist editing UI
9. **LodgingModal.svelte** - Modal for lodging CRUD
10. **TransportationModal.svelte** - Modal for transportation CRUD
11. **NoteModal.svelte** - Modal for note editing
12. **TrailCard.svelte** - Richer trail display (already have basic version)
13. **LocationDropdown.svelte** - Location selector for transportation
14. **CategoryDropdown.svelte** - Category selector with icons
15. **ImmichSelect.svelte** - Immich integration UI

### Specialized Components
16. **LocationDetails.svelte** - Enhanced location detail view
17. **LocationMedia.svelte** - Media gallery for locations
18. **LocationVisits.svelte** - Visit timeline display
19. **CardCarousel.svelte** - Image carousel
20. **AttachmentCard.svelte** / **AttachmentDropdown.svelte** - File attachments
21. **StravaActivityCard.svelte** - Strava integration
22. **WandererCard.svelte** - Wanderer integration
23. **UserCard.svelte** - User display component
24. **Avatar.svelte** - User avatar component

### Utility Components
25. **Toast.svelte** - Better notification system (currently using simple alerts)
26. **DeleteWarning.svelte** - Consistent delete confirmation UI
27. **PointSelectionModal.svelte** - Map-based coordinate selection
28. **TOTPModal.svelte** - Two-factor authentication UI
29. **AboutModal.svelte** - About page content

## 📊 API Consistency Issues

### Response Format Inconsistencies
- Categories returns `List[CategoryResponse]` directly
- Collections returns `CollectionListResponse` with `collections` key
- Locations returns `LocationListResponse` with `locations` key and pagination

### Trailing Slashes
- Backend doesn't require trailing slashes but frontend sometimes adds them
- Should be consistent

## 🚀 Recommended Next Steps

1. **Immediate**: Add update modals for collections, categories, notes
2. **Short-term**: Port MarkdownEditor, ShareModal, TagComplete, ImageManagement
3. **Medium-term**: Add Integrations UI (Immich, Strava, Wanderer)
4. **Long-term**: Port remaining specialized components as needed
