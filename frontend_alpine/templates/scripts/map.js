// Map Methods
const mapMethods = {
    initMap() {
        if (this.map) return;
        
        this.map = L.map('locations-map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        this.updateMapMarkers();
    },

    updateMapMarkers() {
        if (!this.map) return;
        
        // Clear existing markers
        this.markers.forEach(marker => marker.remove());
        this.markers = [];
        
        // Add markers for filtered locations
        const validLocations = this.filteredLocations.filter(loc => 
            loc.latitude && loc.longitude
        );
        
        if (validLocations.length === 0) return;
        
        const bounds = [];
        validLocations.forEach(loc => {
            const marker = L.marker([loc.latitude, loc.longitude]).addTo(this.map);
            marker.bindPopup(`
                <div style="min-width: 200px;">
                    <h4 style="margin: 0 0 0.5rem 0; font-weight: bold;">${loc.name}</h4>
                    ${loc.city || loc.country ? `<p style="margin: 0 0 0.5rem 0; font-size: 0.875rem;">${[loc.city, loc.country].filter(Boolean).join(', ')}</p>` : ''}
                    ${loc.rating ? `<p style="margin: 0; font-size: 0.875rem;">${'⭐'.repeat(loc.rating)}</p>` : ''}
                </div>
            `);
            this.markers.push(marker);
            bounds.push([loc.latitude, loc.longitude]);
        });
        
        // Fit map to show all markers
        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
};
