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
        return this.countryVisitedRegions.some(v => v.region === regionId);
    },

    isCityVisited(cityId) {
        return this.regionVisitedCities.some(v => v.city === cityId);
    },

    countriesWithVisits() {
        // Count unique countries from visited regions using country_id
        const countryIds = new Set();
        this.visitedRegions.forEach(vr => {
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

    clearRegionFilters() {
        this.regionSearchQuery = '';
        this.regionFilterOption = 'all';
    },

    // Computed properties for countries
    get visitedCountriesCount() {
        return this.countries.filter(c => c.num_visits > 0).length;
    },

    get notVisitedCountriesCount() {
        return this.countries.filter(c => c.num_visits === 0).length;
    },

    get completeCountriesCount() {
        return this.countries.filter(c => c.num_visits > 0 && c.num_visits === c.num_regions).length;
    },

    get partialCountriesCount() {
        return this.countries.filter(c => c.num_visits > 0 && c.num_visits < c.num_regions).length;
    },

    get worldSubregions() {
        const subregions = [...new Set(this.countries.map(c => c.subregion))];
        return subregions.filter(s => s && s.trim() !== '').sort();
    },

    get filteredCountries() {
        let filtered = this.countries;

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
        let filtered = this.countryRegions;

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
        if (!this.citySearchQuery) return this.regionCities;
        const query = this.citySearchQuery.toLowerCase();
        return this.regionCities.filter(c => 
            c.name.toLowerCase().includes(query)
        );
    }
};
