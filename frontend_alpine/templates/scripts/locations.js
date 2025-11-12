// Location Methods
const locationMethods = {
    async fetchLocations() {
        const data = await this.api('/locations/');
        this.locations = data.locations || [];
    },

    async createLocation() {
        // Validate form
        if (!this.validateLocationForm()) {
            this.showError('Please fix validation errors before submitting');
            return;
        }
        
        this.loading = true;
        try {
            const payload = { ...this.locationForm };
            if (payload.tags) {
                payload.tags = payload.tags.split(',').map(t => t.trim()).filter(Boolean);
            }
            if (payload.rating) payload.rating = parseInt(payload.rating);
            if (payload.latitude) payload.latitude = parseFloat(payload.latitude);
            if (payload.longitude) payload.longitude = parseFloat(payload.longitude);
            if (payload.category) payload.category = parseInt(payload.category);
            // Note: collection is a UUID string, don't parse as int
            
            // Remove empty fields
            if (!payload.category) delete payload.category;
            if (!payload.collection) delete payload.collection;
            if (!payload.rating) delete payload.rating;
            if (!payload.description) delete payload.description;
            if (!payload.link) delete payload.link;
            
            await this.api('/locations/', { method: 'POST', body: JSON.stringify(payload) });
            await this.fetchLocations();
            this.showAddLocation = false;
            this.locationForm = { name: '', description: '', city: '', country: '', address: '', latitude: null, longitude: null, rating: null, category: '', collection: '', tags: '', is_public: false, link: '' };
            this.validationErrors = {};
            this.showSuccess('Location created!');
        } catch (err) {
            this.showError(err.message);
        } finally {
            this.loading = false;
        }
    },

    startEditLocation() {
        // Pre-fill the form with current location data
        this.locationForm = {
            name: this.selectedLocation.name || '',
            description: this.selectedLocation.description || '',
            city: this.selectedLocation.city || '',
            country: this.selectedLocation.country || '',
            address: this.selectedLocation.address || '',
            state: this.selectedLocation.state || '',
            latitude: this.selectedLocation.latitude || null,
            longitude: this.selectedLocation.longitude || null,
            rating: this.selectedLocation.rating || null,
            category: this.selectedLocation.category?.id || '',
            collection: this.selectedLocation.collection?.id || '',
            tags: this.selectedLocation.tags ? this.selectedLocation.tags.join(', ') : '',
            is_public: this.selectedLocation.is_public || false,
            link: this.selectedLocation.link || ''
        };
        this.editingLocationId = this.selectedLocation.id;
        this.showAddLocation = true;
        this.currentView = 'locations';
    },

    async updateLocation() {
        if (!this.validateLocationForm()) {
            this.showError('Please fix validation errors before submitting');
            return;
        }
        
        this.loading = true;
        try {
            const payload = { ...this.locationForm };
            if (payload.tags) {
                payload.tags = payload.tags.split(',').map(t => t.trim()).filter(Boolean);
            }
            if (payload.rating) payload.rating = parseInt(payload.rating);
            if (payload.latitude) payload.latitude = parseFloat(payload.latitude);
            if (payload.longitude) payload.longitude = parseFloat(payload.longitude);
            if (payload.category) payload.category = parseInt(payload.category);
            
            // Remove empty fields
            if (!payload.category) delete payload.category;
            if (!payload.collection) delete payload.collection;
            if (!payload.rating) delete payload.rating;
            if (!payload.description) delete payload.description;
            if (!payload.link) delete payload.link;
            
            await this.api(`/locations/${this.editingLocationId}`, { 
                method: 'PUT', 
                body: JSON.stringify(payload) 
            });
            await this.fetchLocations();
            this.showAddLocation = false;
            this.editingLocationId = null;
            this.locationForm = { name: '', description: '', city: '', country: '', address: '', latitude: null, longitude: null, rating: null, category: '', collection: '', tags: '', is_public: false, link: '' };
            this.validationErrors = {};
            this.showSuccess('Location updated!');
        } catch (err) {
            this.showError(err.message);
        } finally {
            this.loading = false;
        }
    },

    cancelEdit() {
        this.editingLocationId = null;
        this.showAddLocation = false;
        this.locationForm = { name: '', description: '', city: '', country: '', address: '', latitude: null, longitude: null, rating: null, category: '', collection: '', tags: '', is_public: false, link: '' };
        this.validationErrors = {};
    },

    async deleteLocation(id) {
        if (!confirm('Delete this location?')) return;
        try {
            await this.api(`/locations/${id}`, { method: 'DELETE' });
            await this.fetchLocations();
            if (this.selectedLocation?.id === id) {
                this.selectedLocation = null;
            }
            this.showSuccess('Location deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async viewLocation(location) {
        this.selectedLocation = location;
        this.currentView = 'location-detail';
        this.locationTab = 'notes';
        await Promise.all([
            this.fetchLocationNotes(location.id),
            this.fetchLocationVisits(location.id),
            this.fetchLocationActivities(location.id),
            this.fetchLocationChecklists(location.id),
            this.fetchLocationTransportation(location.id),
            this.fetchLocationLodging(location.id),
            this.fetchLocationTrails(location.id)
        ]);
    },

    // Location sub-resources
    async fetchLocationNotes(locationId) {
        this.locationNotes = await this.api(`/notes/location/${locationId}`);
    },

    async createNote() {
        try {
            await this.api(`/notes/`, {
                method: 'POST',
                body: JSON.stringify({ ...this.noteForm, location: this.selectedLocation.id })
            });
            await this.fetchLocationNotes(this.selectedLocation.id);
            this.showAddNote = false;
            this.noteForm = { name: '', content: '' };
            this.showSuccess('Note created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteNote(noteId) {
        if (!confirm('Delete this note?')) return;
        try {
            await this.api(`/notes/${noteId}`, { method: 'DELETE' });
            await this.fetchLocationNotes(this.selectedLocation.id);
            this.showSuccess('Note deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchLocationActivities(locationId) {
        this.locationActivities = await this.api(`/activities/location/${locationId}`);
    },

    async createActivity() {
        try {
            await this.api(`/activities/`, {
                method: 'POST',
                body: JSON.stringify({ ...this.activityForm, location: this.selectedLocation.id })
            });
            await this.fetchLocationActivities(this.selectedLocation.id);
            this.showAddActivity = false;
            this.activityForm = { type: '', date: '' };
            this.showSuccess('Activity created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteActivity(activityId) {
        if (!confirm('Delete this activity?')) return;
        try {
            await this.api(`/activities/${activityId}`, { method: 'DELETE' });
            await this.fetchLocationActivities(this.selectedLocation.id);
            this.showSuccess('Activity deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchLocationChecklists(locationId) {
        this.locationChecklists = await this.api(`/checklists/location/${locationId}`);
    },

    async createChecklist() {
        try {
            await this.api(`/checklists/`, {
                method: 'POST',
                body: JSON.stringify({ ...this.checklistForm, location: this.selectedLocation.id })
            });
            await this.fetchLocationChecklists(this.selectedLocation.id);
            this.showAddChecklist = false;
            this.checklistForm = { name: '' };
            this.showSuccess('Checklist created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteChecklist(checklistId) {
        if (!confirm('Delete this checklist?')) return;
        try {
            await this.api(`/checklists/${checklistId}`, { method: 'DELETE' });
            await this.fetchLocationChecklists(this.selectedLocation.id);
            this.showSuccess('Checklist deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async createChecklistItem(checklistId) {
        try {
            await this.api(`/checklists/${checklistId}/items`, {
                method: 'POST',
                body: JSON.stringify(this.checklistItemForm)
            });
            await this.fetchLocationChecklists(this.selectedLocation.id);
            this.showAddChecklistItem[checklistId] = false;
            this.checklistItemForm = { name: '' };
            this.showSuccess('Item added!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async toggleChecklistItem(checklistId, itemId) {
        try {
            // Find the item first to toggle its checked state
            const checklist = this.locationChecklists.find(c => c.id === checklistId);
            const item = checklist?.items?.find(i => i.id === itemId);
            if (item) {
                await this.api(`/checklists/items/${itemId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ ...item, checked: !item.checked })
                });
            }
            await this.fetchLocationChecklists(this.selectedLocation.id);
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteChecklistItem(checklistId, itemId) {
        try {
            await this.api(`/checklists/items/${itemId}`, {
                method: 'DELETE'
            });
            await this.fetchLocationChecklists(this.selectedLocation.id);
            this.showSuccess('Item deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchLocationTransportation(locationId) {
        this.locationTransportation = await this.api(`/transportation/location/${locationId}`);
    },

    async createTransportation() {
        try {
            const payload = { ...this.transportationForm, location_id: this.selectedLocation.id };
            if (payload.depart_time === '') delete payload.depart_time;
            if (payload.arrive_time === '') delete payload.arrive_time;
            if (!payload.depart_timezone) delete payload.depart_timezone;
            if (!payload.arrive_timezone) delete payload.arrive_timezone;
            if (!payload.depart_latitude) delete payload.depart_latitude;
            if (!payload.depart_longitude) delete payload.depart_longitude;
            if (!payload.arrive_latitude) delete payload.arrive_latitude;
            if (!payload.arrive_longitude) delete payload.arrive_longitude;
            if (!payload.link) delete payload.link;
            if (!payload.rating) delete payload.rating;
            await this.api(`/transportation/`, {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            await this.fetchLocationTransportation(this.selectedLocation.id);
            this.showAddTransportation = false;
            this.transportationForm = { 
                type: '', from_location: '', to_location: '',
                depart_time: '', arrive_time: '', depart_timezone: '', arrive_timezone: '',
                depart_latitude: null, depart_longitude: null,
                arrive_latitude: null, arrive_longitude: null,
                link: '', rating: null, is_public: false
            };
            this.showSuccess('Transportation created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteTransportation(transportationId) {
        if (!confirm('Delete this transportation?')) return;
        try {
            await this.api(`/transportation/${transportationId}`, { method: 'DELETE' });
            await this.fetchLocationTransportation(this.selectedLocation.id);
            this.showSuccess('Transportation deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchLocationLodging(locationId) {
        this.locationLodging = await this.api(`/lodging/location/${locationId}`);
    },

    async createLodging() {
        try {
            await this.api(`/lodging/`, {
                method: 'POST',
                body: JSON.stringify({ ...this.lodgingForm, location: this.selectedLocation.id })
            });
            await this.fetchLocationLodging(this.selectedLocation.id);
            this.showAddLodging = false;
            this.lodgingForm = { name: '' };
            this.showSuccess('Lodging created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteLodging(lodgingId) {
        if (!confirm('Delete this lodging?')) return;
        try {
            await this.api(`/lodging/${lodgingId}`, { method: 'DELETE' });
            await this.fetchLocationLodging(this.selectedLocation.id);
            this.showSuccess('Lodging deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async fetchLocationTrails(locationId) {
        this.locationTrails = await this.api(`/trails/location/${locationId}`);
    },

    async createTrail() {
        try {
            const payload = { ...this.trailForm, location: this.selectedLocation.id };
            if (payload.length) payload.length = parseFloat(payload.length);
            await this.api(`/trails/`, {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            await this.fetchLocationTrails(this.selectedLocation.id);
            this.showAddTrail = false;
            this.trailForm = { name: '', difficulty: '', length: null };
            this.showSuccess('Trail created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteTrail(trailId) {
        if (!confirm('Delete this trail?')) return;
        try {
            await this.api(`/trails/${trailId}`, { method: 'DELETE' });
            await this.fetchLocationTrails(this.selectedLocation.id);
            this.showSuccess('Trail deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    // Visit methods
    async fetchLocationVisits(locationId) {
        try {
            const data = await this.api(`/visits/?location_id=${locationId}`);
            this.locationVisits = data.visits || [];
        } catch (err) {
            this.showError(err.message);
        }
    },
    async createVisit() {
        try {
            await this.api('/visits/', {
                method: 'POST',
                body: JSON.stringify({
                    location_id: this.selectedLocation.id,
                    start_date: this.visitForm.start_date,
                    end_date: this.visitForm.end_date || null,
                    timezone: this.visitForm.timezone || null,
                    notes: this.visitForm.notes || null
                })
            });
            this.visitForm = { start_date: '', end_date: '', timezone: '', notes: '' };
            this.showAddVisit = false;
            await this.fetchLocationVisits(this.selectedLocation.id);
            this.showSuccess('Visit added!');
        } catch (err) {
            this.showError(err.message);
        }
    },
    async deleteVisit(visitId) {
        try {
            await this.api(`/visits/${visitId}`, { method: 'DELETE' });
            await this.fetchLocationVisits(this.selectedLocation.id);
            this.showSuccess('Visit deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    }
};
