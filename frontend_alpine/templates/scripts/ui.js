// UI Enhancement Methods
const uiMethods = {
    // Theme
    toggleTheme() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
        this.applyTheme();
    },
    
    applyTheme() {
        if (this.darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    },

    // Geolocation
    async getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by your browser');
            return;
        }
        
        this.gettingLocation = true;
        
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            });
            
            this.locationForm.latitude = position.coords.latitude.toFixed(6);
            this.locationForm.longitude = position.coords.longitude.toFixed(6);
            this.showSuccess('Location detected successfully!');
        } catch (error) {
            let message = 'Unable to get your location';
            if (error.code === 1) message = 'Location access denied. Please enable location permissions.';
            else if (error.code === 2) message = 'Location information unavailable.';
            else if (error.code === 3) message = 'Location request timed out.';
            this.showError(message);
        } finally {
            this.gettingLocation = false;
        }
    },
    
    // Tag Suggestions
    get allExistingTags() {
        const tags = new Set();
        this.locations.forEach(loc => {
            if (loc.tags && Array.isArray(loc.tags)) {
                loc.tags.forEach(tag => tags.add(tag.toLowerCase()));
            }
        });
        return Array.from(tags).sort();
    },
    
    get tagSuggestions() {
        if (!this.locationForm.tags) return this.allExistingTags;
        const currentTags = this.locationForm.tags.split(',').map(t => t.trim().toLowerCase());
        const lastTag = currentTags[currentTags.length - 1];
        
        if (!lastTag) return this.allExistingTags;
        
        return this.allExistingTags.filter(tag => 
            tag.includes(lastTag) && !currentTags.slice(0, -1).includes(tag)
        );
    },
    
    addTagSuggestion(tag) {
        const currentTags = this.locationForm.tags.split(',').map(t => t.trim()).filter(Boolean);
        currentTags.pop(); // Remove incomplete tag
        currentTags.push(tag);
        this.locationForm.tags = currentTags.join(', ') + ', ';
        this.showTagSuggestions = false;
    },
    
    // Address Autocomplete
    async searchAddress(query) {
        if (!query || query.length < 3) {
            this.addressSuggestions = [];
            this.showAddressSuggestions = false;
            return;
        }
        
        this.searchingAddress = true;
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`,
                { headers: { 'User-Agent': 'AdventureLog' } }
            );
            const results = await response.json();
            this.addressSuggestions = results.map(r => ({
                display: r.display_name,
                lat: parseFloat(r.lat),
                lon: parseFloat(r.lon),
                address: r.display_name
            }));
            this.showAddressSuggestions = this.addressSuggestions.length > 0;
        } catch (err) {
            console.error('Address search error:', err);
            this.addressSuggestions = [];
        } finally {
            this.searchingAddress = false;
        }
    },
    
    selectAddress(suggestion) {
        this.locationForm.address = suggestion.address;
        this.locationForm.latitude = suggestion.lat.toFixed(6);
        this.locationForm.longitude = suggestion.lon.toFixed(6);
        
        // Auto-fill city and country if empty
        const parts = suggestion.display.split(', ');
        if (!this.locationForm.city && parts.length > 2) {
            this.locationForm.city = parts[parts.length - 3];
        }
        if (!this.locationForm.country && parts.length > 0) {
            this.locationForm.country = parts[parts.length - 1];
        }
        
        this.showAddressSuggestions = false;
        this.showSuccess('Address selected!');
    },

    // Form Validation
    validateLocationForm() {
        this.validationErrors = {};
        
        if (!this.locationForm.name || this.locationForm.name.trim().length === 0) {
            this.validationErrors.name = 'Name is required';
        } else if (this.locationForm.name.length > 200) {
            this.validationErrors.name = 'Name must be less than 200 characters';
        }
        
        if (this.locationForm.latitude !== null && this.locationForm.latitude !== '') {
            const lat = parseFloat(this.locationForm.latitude);
            if (isNaN(lat) || lat < -90 || lat > 90) {
                this.validationErrors.latitude = 'Latitude must be between -90 and 90';
            }
        }
        
        if (this.locationForm.longitude !== null && this.locationForm.longitude !== '') {
            const lon = parseFloat(this.locationForm.longitude);
            if (isNaN(lon) || lon < -180 || lon > 180) {
                this.validationErrors.longitude = 'Longitude must be between -180 and 180';
            }
        }
        
        if (this.locationForm.rating && (parseInt(this.locationForm.rating) < 1 || parseInt(this.locationForm.rating) > 5)) {
            this.validationErrors.rating = 'Rating must be between 1 and 5';
        }
        
        return Object.keys(this.validationErrors).length === 0;
    },
    
    clearValidationError(field) {
        delete this.validationErrors[field];
    },

    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + N to add location (when on locations view and logged in)
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                if (this.currentView === 'locations' && this.user) {
                    e.preventDefault();
                    this.showAddLocation = !this.showAddLocation;
                    // Focus on name field after a brief delay
                    if (this.showAddLocation) {
                        setTimeout(() => {
                            const nameInput = document.querySelector('input[x-model="locationForm.name"]');
                            if (nameInput) nameInput.focus();
                        }, 100);
                    }
                }
            }
            
            // Escape to close forms
            if (e.key === 'Escape') {
                if (this.showAddLocation) this.showAddLocation = false;
                if (this.showAddCollection) this.showAddCollection = false;
                if (this.showAddCategory) this.showAddCategory = false;
            }
        });
    }
};
