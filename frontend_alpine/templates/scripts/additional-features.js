// Additional features JavaScript methods
// FastAPI migration adjustments:
// - Disabled legacy features pointing to missing endpoints (search, calendar, profile CRUD)
// - Corrected import/export paths to /api/data/... (frontend uses API_URL + /data)
// - Stubs provide user feedback without throwing network errors

const additionalFeaturesMethods = {
    // ---- Disabled / Stubbed Features ----
    performSearch() {
        this.showError('Search feature not available (backend endpoint missing)');
        this.searchResults = null;
        this.searchResultsCount = 0;
    },
    loadCalendarEvents() {
        this.showError('Calendar feature not available (backend endpoint missing)');
        this.calendarEvents = [];
        this.calendarDays = [];
    },
    downloadICS() {
        this.showError('ICS export not available (backend endpoint missing)');
    },
    updateProfile() {
        this.showError('Profile update not available (backend endpoint missing)');
    },
    deleteAccount() {
        this.showError('Account deletion not available (backend endpoint missing)');
    },
    loadProfile(userId) {
        this.showError('Profile view not available (backend endpoint missing)');
        this.profileUser = null;
    },
    loadProfileStats(userId) { /* stub */ },
    loadProfileLocations(userId) { /* stub */ },
    loadProfileCollections(userId) { /* stub */ },
    viewProfile(userId) {
        this.currentView = 'profile';
        this.loadProfile(userId);
    },

    // ---- Data Import / Export (active) ----
    async exportData() {
        try {
            const response = await fetch(`${API_URL}/data/export/json`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!response.ok) {
                this.showError('Failed to export data');
                return;
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `adventurelog-export-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            this.showSuccess('Data exported successfully');
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export data');
        }
    },

    async importData(event) {
        const file = event.target.files?.[0];
        if (!file) return;
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            const response = await fetch(`${API_URL}/data/import/json`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                this.showError(error.detail || 'Import failed');
                return;
            }
            const stats = await response.json();
            const message = `Import complete: ${stats.locations_imported} locations, ${stats.collections_imported} collections, ${stats.categories_imported} categories, ${stats.visits_imported} visits`;
            if (stats.errors?.length) {
                console.warn('Import errors:', stats.errors);
            }
            this.showSuccess(message);
            await Promise.all([
                this.fetchLocations?.(),
                this.fetchCollections?.(),
                this.fetchCategories?.(),
                this.fetchStats?.(),
                this.fetchAllVisits?.()
            ]);
        } catch (error) {
            console.error('Import error:', error);
            this.showError('Failed to import data: ' + error.message);
        } finally {
            event.target.value = '';
        }
    },

    confirmDeleteAccount() {
        this.showError('Account deletion disabled (backend endpoint missing)');
    },

    // ---- Navigation helpers ----
    viewWorldTravel() {
        this.currentView = 'worldtravel';
        this.worldTravelMode = 'countries';
        if (!this.countries || this.countries.length === 0) {
            this.fetchCountries?.();
            this.fetchVisitedRegions?.();
            this.fetchVisitedCities?.();
        }
    },
    viewCollections() {
        this.currentView = 'collections';
        if (!this.collections || this.collections.length === 0) {
            this.fetchCollections?.();
        }
    }
};

// Export for integration
// (Assumes a bundling/merging step combines these methods into the main app object.)
if (typeof window !== 'undefined') {
    window.additionalFeaturesMethods = additionalFeaturesMethods;
}
