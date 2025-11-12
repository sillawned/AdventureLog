// Main App - Combines all modules
function app() {
    return {
        // Initialize state
        ...getInitialState(),
        
        // Lifecycle
        async init() {
            // Load theme preference
            this.darkMode = localStorage.getItem('darkMode') === 'true';
            this.applyTheme();
            
            this.token = localStorage.getItem('token');
            if (this.token) {
                await this.fetchUser();
                if (this.user) {
                    this.currentView = 'dashboard';
                    await Promise.all([
                        this.fetchStats(),
                        this.fetchLocations(),
                        this.fetchCollections(),
                        this.fetchCategories(),
                        this.fetchAllVisits(),
                        this.fetchCountries(),
                        this.fetchVisitedRegions(),
                        this.fetchVisitedCities()
                    ]);
                }
            }
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
        },
        
        // Computed properties from filters
        get filteredLocations() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'filteredLocations').get;
            return getter.call(this);
        },
        
        get filteredCollections() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'filteredCollections').get;
            return getter.call(this);
        },
        
        get filteredCategories() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'filteredCategories').get;
            return getter.call(this);
        },
        
        get paginatedLocations() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'paginatedLocations').get;
            return getter.call(this);
        },
        
        get totalPages() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'totalPages').get;
            return getter.call(this);
        },
        
        get pageNumbers() {
            const getter = Object.getOwnPropertyDescriptor(filterMethods, 'pageNumbers').get;
            return getter.call(this);
        },
        
        // Computed properties from ui
        get allExistingTags() {
            const getter = Object.getOwnPropertyDescriptor(uiMethods, 'allExistingTags').get;
            return getter.call(this);
        },
        
        get tagSuggestions() {
            const getter = Object.getOwnPropertyDescriptor(uiMethods, 'tagSuggestions').get;
            return getter.call(this);
        },
        
        // Merge all methods
        ...apiMethods,
        ...authMethods,
        ...locationMethods,
        ...collectionMethods,
        ...worldTravelMethods,
        ...mapMethods,
        ...statsMethods,
        
        // UI methods (exclude computed properties)
        toggleTheme: uiMethods.toggleTheme,
        applyTheme: uiMethods.applyTheme,
        getCurrentLocation: uiMethods.getCurrentLocation,
        addTagSuggestion: uiMethods.addTagSuggestion,
        searchAddress: uiMethods.searchAddress,
        selectAddress: uiMethods.selectAddress,
        validateLocationForm: uiMethods.validateLocationForm,
        clearValidationError: uiMethods.clearValidationError,
        setupKeyboardShortcuts: uiMethods.setupKeyboardShortcuts,
        
        // Filter methods (exclude computed properties)
        clearFilters: filterMethods.clearFilters,
        changePage: filterMethods.changePage,
        
        // Additional computed properties
        get currentMonthYear() {
            return this.calendarCurrentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        },
        
        get filteredCalendarEvents() {
            if (!this.calendarSearchFilter) return this.calendarEvents || [];
            const query = this.calendarSearchFilter.toLowerCase();
            return (this.calendarEvents || []).filter(event => 
                event.title?.toLowerCase().includes(query) ||
                event.location?.toLowerCase().includes(query)
            );
        }
    };
}
