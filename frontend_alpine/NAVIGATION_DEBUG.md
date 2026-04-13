# Navigation Debug Guide

## Testing Navigation Issues

The views (Collections, World Travel, Search, Calendar, Settings) should work. Here's how to debug:

### 1. Open Browser Console
Press F12 and check for JavaScript errors

### 2. Test View Switching
After logging in, try these in the browser console:

```javascript
// Check if app is loaded
console.log('Alpine data:', Alpine.$data(document.querySelector('[x-data]')));

// Manually switch to collections view
let app = Alpine.$data(document.querySelector('[x-data]'));
app.currentView = 'collections';
console.log('Current view:', app.currentView);
console.log('Collections data:', app.collections);

// Try world travel
app.currentView = 'worldtravel';
console.log('Countries:', app.countries);

// Try search
app.currentView = 'search';

// Try calendar
app.currentView = 'calendar';

// Try settings
app.currentView = 'settings';
```

### 3. Check Data Loading
```javascript
let app = Alpine.$data(document.querySelector('[x-data]'));

// Check if data loaded
console.log('Collections:', app.collections);
console.log('Countries:', app.countries);
console.log('Locations:', app.locations);
```

### 4. Common Issues

#### Issue: Views are blank
**Cause:** Data not loaded
**Fix:** Check if init() completed successfully
```javascript
let app = Alpine.$data(document.querySelector('[x-data]'));
// Manually fetch data
await app.fetchCollections();
await app.fetchCountries();
```

#### Issue: Clicking nav links does nothing
**Cause:** Alpine not initialized or currentView not reactive
**Fix:** Check console for Alpine errors

#### Issue: "performSearch is not defined" or similar
**Cause:** Method not properly spread in app-modular.js
**Fix:** Verify all method objects are imported

### 5. Manual Navigation Test
Click the navigation links and watch the console. You should see:
- No errors
- currentView changing
- Views appearing/disappearing with x-show

### 6. Check if x-show is working
```javascript
// In console, force a view to show
document.querySelector('[x-show="currentView === \'collections\'"]').style.display = 'block';
```

### 7. Verify Methods Exist
```javascript
let app = Alpine.$data(document.querySelector('[x-data]'));
console.log('Has fetchCollections:', typeof app.fetchCollections);
console.log('Has viewCollections:', typeof app.viewCollections);
console.log('Has fetchCountries:', typeof app.fetchCountries);
console.log('Has performSearch:', typeof app.performSearch);
console.log('Has loadCalendarEvents:', typeof app.loadCalendarEvents);
```

## Expected Behavior

When you click:
- **Collections**: Should show list of collections (may be empty if none created)
- **World Travel**: Should show country list with visit counts
- **Search**: Should show search bar (search is stubbed but UI works)
- **Calendar**: Should show calendar view (feature stubbed but UI works)
- **Settings**: Should show settings sections

## If Still Not Working

1. Check browser console for specific errors
2. Verify you're logged in (token in localStorage)
3. Check Network tab for failed API calls
4. Run the FastAPI backend with `--reload` flag to see server logs

## Quick Fix Commands

If views truly don't work, try:

```bash
# Clear browser cache and localStorage
# In browser console:
localStorage.clear();
location.reload();

# Or rebuild frontend
cd /home/user/workspace/AdventureLog
./rebuild.sh
```
