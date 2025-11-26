// WorldTravel Methods
const worldTravelMethods = {
    async fetchCountries() {
        try {
            this.countries = await this.api('/worldtravel/countries/');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchVisitedRegions() {
        try {
            this.visitedRegions = await this.api('/worldtravel/visited-regions/');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchVisitedCities() {
        try {
            this.visitedCities = await this.api('/worldtravel/visited-cities/');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async viewCountryDetails(country) {
        this.selectedCountry = country;
        this.worldTravelMode = 'country-detail';
        this.regionSearchQuery = '';
        
        try {
            // Fetch regions and visits for this country
            const [regions, visits] = await Promise.all([
                this.api(`/worldtravel/countries/${country.country_code}/regions/`),
                this.api(`/worldtravel/countries/${country.country_code}/visits/`)
            ]);
            
            this.countryRegions = regions;
            this.countryVisitedRegions = visits;
        } catch (err) {
            this.showError(err.message);
        }
    },

    async viewRegionCities(region) {
        this.selectedRegion = region;
        this.worldTravelMode = 'region-cities';
        this.citySearchQuery = '';
        
        try {
            // Fetch cities and visits for this region
            const [cities, visits] = await Promise.all([
                this.api(`/worldtravel/regions/${region.id}/cities/`),
                this.api(`/worldtravel/regions/${region.id}/visits/`)
            ]);
            
            this.regionCities = cities;
            this.regionVisitedCities = visits;
        } catch (err) {
            this.showError(err.message);
        }
    },

    async markRegionVisited(regionId) {
        try {
            await this.api('/worldtravel/visited-regions/', {
                method: 'POST',
                body: JSON.stringify({ region: regionId })
            });
            
            await this.fetchVisitedRegions();
            
            // Refresh country visits if viewing country
            if (this.selectedCountry) {
                const visits = await this.api(`/worldtravel/countries/${this.selectedCountry.country_code}/visits/`);
                this.countryVisitedRegions = visits;
            }
            
            this.showSuccess('Region marked as visited!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async unmarkRegionVisited(regionId) {
        try {
            await this.api(`/worldtravel/visited-regions/${regionId}`, {
                method: 'DELETE'
            });
            
            await this.fetchVisitedRegions();
            
            // Refresh country visits if viewing country
            if (this.selectedCountry) {
                const visits = await this.api(`/worldtravel/countries/${this.selectedCountry.country_code}/visits/`);
                this.countryVisitedRegions = visits;
            }
            
            this.showSuccess('Region unmarked!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async markCityVisited(cityId) {
        try {
            await this.api('/worldtravel/visited-cities/', {
                method: 'POST',
                body: JSON.stringify({ city: cityId })
            });
            
            await Promise.all([
                this.fetchVisitedCities(),
                this.fetchVisitedRegions()  // Cities auto-mark regions
            ]);
            
            // Refresh region visits if viewing region
            if (this.selectedRegion) {
                const visits = await this.api(`/worldtravel/regions/${this.selectedRegion.id}/visits/`);
                this.regionVisitedCities = visits;
            }
            
            this.showSuccess('City marked as visited!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async unmarkCityVisited(cityId) {
        try {
            await this.api(`/worldtravel/visited-cities/${cityId}`, {
                method: 'DELETE'
            });
            
            await this.fetchVisitedCities();
            
            // Refresh region visits if viewing region
            if (this.selectedRegion) {
                const visits = await this.api(`/worldtravel/regions/${this.selectedRegion.id}/visits/`);
                this.regionVisitedCities = visits;
            }
            
            this.showSuccess('City unmarked!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    // Helper methods
    isRegionVisited(regionId) {
        return (this.countryVisitedRegions || []).some(v => v.region === regionId);
    },

    isCityVisited(cityId) {
        return (this.regionVisitedCities || []).some(v => v.city === cityId);
    },

    countriesWithVisits() {
        // Count unique countries from visited regions using country_id
        const countryIds = new Set();
        (this.visitedRegions || []).forEach(vr => {
            if (vr.country_id) {
                countryIds.add(vr.country_id);
            }
        });
        return countryIds.size;
    },

    clearWorldTravelFilters() {
        this.worldTravelSearchQuery = '';
        this.worldTravelFilterOption = 'all';
        this.worldSubregionFilter = '';
    },

    // World Travel Map Management
    worldTravelMapInstance: null,
    worldTravelMapMarkers: [],

    initWorldTravelMap() {
        try {
            const mapElement = document.getElementById('world-travel-map');
            if (!mapElement) return;

            if (this.worldTravelMapInstance) {
                // Map already exists, just invalidate size and update markers
                setTimeout(() => {
                    this.worldTravelMapInstance.invalidateSize();
                    this.updateWorldTravelMapMarkers();
                }, 100);
                return;
            }

            // Initialize Leaflet map
            this.worldTravelMapInstance = L.map('world-travel-map').setView([20, 0], 2);

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.worldTravelMapInstance);

            // Add markers
            this.updateWorldTravelMapMarkers();
        } catch (error) {
            console.error('World Travel map initialization error:', error);
        }
    },

    updateWorldTravelMapMarkers() {
        if (!this.worldTravelMapInstance) {
            console.log('World Travel map instance not initialized');
            return;
        }

        // Clear existing markers
        this.worldTravelMapMarkers.forEach(marker => this.worldTravelMapInstance.removeLayer(marker));
        this.worldTravelMapMarkers = [];

        // Get filtered countries with coordinates
        const filtered = this.filteredCountries.filter(c => c.latitude && c.longitude);
        console.log(`World Travel map: ${filtered.length} countries with coordinates`);

        // Add markers for each country
        filtered.forEach(country => {
            // Determine marker color based on visit status
            let color;
            if (country.num_visits === 0) {
                color = '#f87171'; // Red - not visited
            } else if (country.num_visits === country.num_regions && country.num_regions > 0) {
                color = '#10b981'; // Green - complete
            } else {
                color = '#60a5fa'; // Blue - partial
            }

            const icon = L.divIcon({
                html: `<div style="background: ${color}; color: white; padding: 4px 8px; border-radius: 12px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); font-size: 12px; font-weight: 600; white-space: nowrap;">${country.name}</div>`,
                className: 'custom-marker',
                iconSize: [0, 0]
            });

            const marker = L.marker([country.latitude, country.longitude], { icon })
                .addTo(this.worldTravelMapInstance);

            // Create popup content
            let statusBadge;
            if (country.num_visits === 0) {
                statusBadge = '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">Not Visited</span>';
            } else if (country.num_visits === country.num_regions && country.num_regions > 0) {
                statusBadge = '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">✓ Complete</span>';
            } else {
                statusBadge = '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">Partial</span>';
            }

            const popupContent = `
                <div style="min-width: 200px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <img src="https://flagpedia.net/data/flags/w580/${country.country_code.toLowerCase()}.webp" 
                             alt="${country.name}" 
                             style="width: 32px; height: 24px; border-radius: 4px; object-fit: cover;"
                             onerror="this.style.display='none'">
                        <h3 style="font-weight: bold; margin: 0;">${country.name}</h3>
                    </div>
                    <div style="margin-bottom: 8px;">
                        ${statusBadge}
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                        <div>${country.num_regions} regions • ${country.num_visits} visited</div>
                        ${country.capital ? `<div>Capital: ${country.capital}</div>` : ''}
                    </div>
                    <button onclick="window.viewCountryFromMap('${country.country_code}')" 
                            style="background: var(--primary, #3b82f6); color: white; padding: 6px 12px; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; width: 100%;">
                        View Details
                    </button>
                </div>
            `;

            marker.bindPopup(popupContent);
            this.worldTravelMapMarkers.push(marker);
        });

        // Fit bounds if there are markers
        if (this.worldTravelMapMarkers.length > 0) {
            const group = L.featureGroup(this.worldTravelMapMarkers);
            this.worldTravelMapInstance.fitBounds(group.getBounds().pad(0.1));
        }
    },

    clearRegionFilters() {
        this.regionSearchQuery = '';
        this.regionFilterOption = 'all';
    },

    // Computed properties for countries
    get visitedCountriesCount() {
        return (this.countries || []).filter(c => c.num_visits > 0).length;
    },

    get notVisitedCountriesCount() {
        return (this.countries || []).filter(c => c.num_visits === 0).length;
    },

    get completeCountriesCount() {
        return (this.countries || []).filter(c => c.num_visits > 0 && c.num_visits === c.num_regions).length;
    },

    get partialCountriesCount() {
        return (this.countries || []).filter(c => c.num_visits > 0 && c.num_visits < c.num_regions).length;
    },

    get worldSubregions() {
        const subregions = [...new Set((this.countries || []).map(c => c.subregion))];
        return subregions.filter(s => s && s.trim() !== '').sort();
    },

    get filteredCountries() {
        let filtered = this.countries || [];

        // Apply search filter
        if (this.worldTravelSearchQuery) {
            const query = this.worldTravelSearchQuery.toLowerCase();
            filtered = filtered.filter(c => 
                c.name.toLowerCase().includes(query) ||
                c.country_code.toLowerCase().includes(query) ||
                (c.capital && c.capital.toLowerCase().includes(query))
            );
        }

        // Apply status filter
        if (this.worldTravelFilterOption === 'complete') {
            filtered = filtered.filter(c => c.num_visits > 0 && c.num_visits === c.num_regions);
        } else if (this.worldTravelFilterOption === 'partial') {
            filtered = filtered.filter(c => c.num_visits > 0 && c.num_visits < c.num_regions);
        } else if (this.worldTravelFilterOption === 'not') {
            filtered = filtered.filter(c => c.num_visits === 0);
        }

        // Apply subregion filter
        if (this.worldSubregionFilter) {
            filtered = filtered.filter(c => c.subregion === this.worldSubregionFilter);
        }

        return filtered;
    },

    get filteredRegions() {
        let filtered = this.countryRegions || [];

        // Apply search filter
        if (this.regionSearchQuery) {
            const query = this.regionSearchQuery.toLowerCase();
            filtered = filtered.filter(r => 
                r.name.toLowerCase().includes(query)
            );
        }

        // Apply visited filter
        if (this.regionFilterOption === 'visited') {
            filtered = filtered.filter(r => 
                this.countryVisitedRegions.some(vr => vr.region === r.id)
            );
        } else if (this.regionFilterOption === 'not-visited') {
            filtered = filtered.filter(r => 
                !this.countryVisitedRegions.some(vr => vr.region === r.id)
            );
        }

        return filtered;
    },

    get filteredCities() {
        if (!this.citySearchQuery) return this.regionCities || [];
        const query = this.citySearchQuery.toLowerCase();
        return (this.regionCities || []).filter(c => 
            c.name.toLowerCase().includes(query)
        );
    }
};

// Helper function for world travel map popup buttons
window.viewCountryFromMap = function(countryCode) {
    const appElement = document.querySelector('[x-data]');
    if (appElement) {
        const alpine = Alpine.$data(appElement);
        alpine.viewCountryDetails({ country_code: countryCode });
    }
};
