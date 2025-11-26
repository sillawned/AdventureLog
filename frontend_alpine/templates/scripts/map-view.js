// Map view JavaScript methods
const mapViewMethods = {
    // Map state
    map: null,
    markers: [],
    mapShowVisited: true,
    mapShowPlanned: true,

    // Initialize map
    async initMap() {
        if (this.map) return; // Already initialized

        try {
            // Initialize Leaflet map
            this.map = L.map('locations-map').setView([20, 0], 2);

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // Add markers for locations
            this.updateMapMarkers();
        } catch (error) {
            console.error('Map initialization error:', error);
        }
    },

    // Update markers on map
    updateMapMarkers() {
        if (!this.map) return;

        // Clear existing markers
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];

        // Get filtered locations
        const filtered = this.locations.filter(loc => {
            if (!loc.latitude || !loc.longitude) return false;
            if (loc.is_visited && !this.mapShowVisited) return false;
            if (!loc.is_visited && !this.mapShowPlanned) return false;
            return true;
        });

        // Add markers
        filtered.forEach(location => {
            const icon = L.divIcon({
                html: `<div style="background: ${location.is_visited ? '#f87171' : '#60a5fa'}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${location.category?.icon || '📍'}</div>`,
                className: 'custom-marker',
                iconSize: [32, 32]
            });

            const marker = L.marker([location.latitude, location.longitude], { icon })
                .addTo(this.map);

            // Create popup content
            let popupContent = `
                <div style="min-width: 200px;">
                    <h3 style="font-weight: bold; margin-bottom: 8px;">${location.name}</h3>
                    <div style="margin-bottom: 8px;">
                        <span style="background: ${location.is_visited ? '#10b981' : '#3b82f6'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                            ${location.is_visited ? 'Visited' : 'Planned'}
                        </span>
            `;

            if (location.category) {
                popupContent += `
                        <span style="border: 1px solid #e5e7eb; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 4px;">
                            ${location.category.icon} ${location.category.display_name}
                        </span>
                `;
            }

            popupContent += `
                    </div>
                    <button onclick="window.viewLocationFromMap('${location.id}')" style="background: var(--primary); color: white; padding: 6px 12px; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; margin-top: 8px;">
                        View Details
                    </button>
                </div>
            `;

            marker.bindPopup(popupContent);
            this.markers.push(marker);
        });

        // Fit bounds if there are markers
        if (this.markers.length > 0) {
            const group = L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    },

    // Open new location modal
    openNewLocationModal() {
        this.currentView = 'locations';
        this.showNewLocationModal = true;
    }
};

// Helper function to view location from map popup
window.viewLocationFromMap = function(locationId) {
    const appElement = document.querySelector('[x-data]');
    if (appElement) {
        const alpine = Alpine.$data(appElement);
        alpine.viewLocation(locationId);
    }
};
