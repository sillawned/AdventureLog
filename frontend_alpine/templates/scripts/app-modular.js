// Main App - Combines all modules with error-safe getters
function app() {
    try {
        const state = getInitialState();
        
        // Helper to create safe getters
        function safeGetter(name, fn) {
            return {
                get() {
                    try {
                        return fn.call(this);
                    } catch (error) {
                        console.warn(`Error in getter ${name}:`, error);
                        return Array.isArray(this[name]) ? [] : null;
                    }
                }
            };
        }
        
        const appObject = {
            ...state,
            
            async init() {
                try {
                    console.log('Alpine.js initializing...');
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
                    
                    this.setupKeyboardShortcuts();
                    console.log('Alpine.js initialized successfully');
                } catch (error) {
                    console.error('Error during Alpine initialization:', error);
                }
            },
            
            // Spread all methods
            ...apiMethods,
            ...authMethods,
            ...locationMethods,
            ...collectionMethods,
            ...worldTravelMethods,
            ...additionalFeaturesMethods,
            ...mapViewMethods,
            ...mapMethods,
            ...statsMethods,
            
            // UI methods  
            toggleTheme: uiMethods.toggleTheme,
            applyTheme: uiMethods.applyTheme,
            getCurrentLocation: uiMethods.getCurrentLocation,
            addTagSuggestion: uiMethods.addTagSuggestion,
            searchAddress: uiMethods.searchAddress,
            selectAddress: uiMethods.selectAddress,
            validateLocationForm: uiMethods.validateLocationForm,
            clearValidationError: uiMethods.clearValidationError,
            setupKeyboardShortcuts: uiMethods.setupKeyboardShortcuts,
            
            // Filter methods
            clearFilters: filterMethods.clearFilters,
            changePage: filterMethods.changePage,
        };
        
        // Add all getters as properties using Object.defineProperty for safety
        // This way Alpine won't throw errors during reactive setup
        const getters = {
            filteredLocations() {
                if (!Array.isArray(this.locations)) return [];
                let filtered = this.locations.slice();
                if (this.searchQuery) {
                    const query = this.searchQuery.toLowerCase();
                    filtered = filtered.filter(loc => 
                        loc.name?.toLowerCase().includes(query) ||
                        loc.city?.toLowerCase().includes(query) ||
                        loc.country?.toLowerCase().includes(query) ||
                        (loc.tags && loc.tags.some(tag => tag.toLowerCase().includes(query)))
                    );
                }
                if (this.filterCategory) {
                    filtered = filtered.filter(loc => loc.category?.id === parseInt(this.filterCategory));
                }
                if (this.filterCollection) {
                    filtered = filtered.filter(loc => loc.collection?.id === this.filterCollection);
                }
                if (this.filterRating) {
                    filtered = filtered.filter(loc => loc.rating === parseInt(this.filterRating));
                }
                switch (this.sortBy) {
                    case 'name':
                        filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
                        break;
                    case 'rating-high':
                        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
                        break;
                    case 'rating-low':
                        filtered.sort((a, b) => (a.rating || 0) - (b.rating || 0));
                        break;
                    case 'date-new':
                        filtered.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
                        break;
                    case 'date-old':
                        filtered.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
                        break;
                }
                return filtered;
            },
            
            filteredCollections() {
                if (!this.collectionsSearchQuery) return this.collections || [];
                const query = this.collectionsSearchQuery.toLowerCase();
                return (this.collections || []).filter(col => col.name?.toLowerCase().includes(query));
            },
            
            filteredCategories() {
                if (!this.categoriesSearchQuery) return this.categories || [];
                const query = this.categoriesSearchQuery.toLowerCase();
                return (this.categories || []).filter(cat => 
                    cat.name?.toLowerCase().includes(query) ||
                    cat.icon?.toLowerCase().includes(query)
                );
            },
            
            paginatedLocations() {
                const start = (this.currentPage - 1) * this.itemsPerPage;
                const end = start + this.itemsPerPage;
                return this.filteredLocations.slice(start, end);
            },
            
            totalPages() {
                return Math.ceil(this.filteredLocations.length / this.itemsPerPage);
            },
            
            pageNumbers() {
                const pages = [];
                const total = this.totalPages;
                const current = this.currentPage;
                if (total <= 7) {
                    for (let i = 1; i <= total; i++) pages.push(i);
                } else {
                    pages.push(1);
                    if (current > 3) pages.push('...');
                    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
                        pages.push(i);
                    }
                    if (current < total - 2) pages.push('...');
                    pages.push(total);
                }
                return pages;
            },
            
            allExistingTags() {
                const tags = new Set();
                (this.locations || []).forEach(loc => {
                    if (loc.tags) {
                        loc.tags.forEach(tag => tags.add(tag));
                    }
                });
                return Array.from(tags);
            },
            
            tagSuggestions() {
                if (!this.locationForm.tags) return this.allExistingTags;
                const currentTags = this.locationForm.tags.split(',').map(t => t.trim());
                const lastTag = currentTags[currentTags.length - 1].toLowerCase();
                if (!lastTag) return this.allExistingTags;
                return this.allExistingTags.filter(tag => 
                    tag.toLowerCase().includes(lastTag) && !currentTags.includes(tag)
                );
            },
            
            // WorldTravel getters
            filteredCountries() {
                let filtered = this.countries || [];
                if (this.worldTravelSearchQuery) {
                    const query = this.worldTravelSearchQuery.toLowerCase();
                    filtered = filtered.filter(c => 
                        c.name.toLowerCase().includes(query) ||
                        c.country_code.toLowerCase().includes(query) ||
                        (c.capital && c.capital.toLowerCase().includes(query))
                    );
                }
                if (this.worldTravelFilterOption === 'complete') {
                    filtered = filtered.filter(c => c.num_visits > 0 && c.num_visits === c.num_regions);
                } else if (this.worldTravelFilterOption === 'partial') {
                    filtered = filtered.filter(c => c.num_visits > 0 && c.num_visits < c.num_regions);
                } else if (this.worldTravelFilterOption === 'not') {
                    filtered = filtered.filter(c => c.num_visits === 0);
                }
                if (this.worldSubregionFilter) {
                    filtered = filtered.filter(c => c.subregion === this.worldSubregionFilter);
                }
                return filtered;
            },
            
            filteredRegions() {
                let filtered = this.countryRegions || [];
                if (this.regionSearchQuery) {
                    const query = this.regionSearchQuery.toLowerCase();
                    filtered = filtered.filter(r => r.name.toLowerCase().includes(query));
                }
                const visitedRegions = this.countryVisitedRegions || [];
                if (this.regionFilterOption === 'visited') {
                    filtered = filtered.filter(r => 
                        visitedRegions.some(vr => vr.region === r.id)
                    );
                } else if (this.regionFilterOption === 'not-visited') {
                    filtered = filtered.filter(r => 
                        !visitedRegions.some(vr => vr.region === r.id)
                    );
                }
                return filtered;
            },
            
            filteredCities() {
                if (!this.citySearchQuery) return this.regionCities || [];
                const query = this.citySearchQuery.toLowerCase();
                return (this.regionCities || []).filter(c => c.name.toLowerCase().includes(query));
            },
            
            visitedCountriesCount() {
                return (this.countries || []).filter(c => c.num_visits > 0).length;
            },
            
            notVisitedCountriesCount() {
                return (this.countries || []).filter(c => c.num_visits === 0).length;
            },
            
            allSubregions() {
                const subregions = [...new Set((this.countries || []).map(c => c.subregion))];
                return subregions.filter(s => s && s.trim() !== '').sort();
            },
            
            completeCountriesCount() {
                return (this.countries || []).filter(c => c.num_visits > 0 && c.num_visits === c.num_regions).length;
            },
            
            partialCountriesCount() {
                return (this.countries || []).filter(c => c.num_visits > 0 && c.num_visits < c.num_regions).length;
            },
            
            worldSubregions() {
                const subregions = [...new Set((this.countries || []).map(c => c.subregion))];
                return subregions.filter(s => s && s.trim() !== '').sort();
            },
            
            currentMonthYear() {
                try {
                    return (this.calendarCurrentDate || new Date()).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
                } catch (e) {
                    return '';
                }
            },
            
            filteredCalendarEvents() {
                if (!this.calendarSearchFilter) return this.calendarEvents || [];
                const query = this.calendarSearchFilter.toLowerCase();
                return (this.calendarEvents || []).filter(event => 
                    event.title?.toLowerCase().includes(query) ||
                    event.location?.toLowerCase().includes(query)
                );
            }
        };
        
        // Add each getter as a property with safe wrapping
        Object.keys(getters).forEach(key => {
            Object.defineProperty(appObject, key, {
                get() {
                    try {
                        return getters[key].call(this);
                    } catch (error) {
                        console.warn(`Getter error in ${key}:`, error.message);
                        return [];
                    }
                },
                enumerable: true,
                configurable: true
            });
        });
        
        return appObject;
    } catch (error) {
        console.error('Fatal error creating Alpine app:', error);
        return {
            ...getInitialState(),
            init() {
                console.error('App failed to initialize properly');
            }
        };
    }
}
