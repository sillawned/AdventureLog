// Collection and Category Methods
const collectionMethods = {
    async fetchCollections() {
        const data = await this.api('/collections/');
        this.collections = data.collections || [];
    },

    async createCollection() {
        try {
            const payload = { ...this.collectionForm };
            if (!payload.description) delete payload.description;
            if (!payload.start_date) delete payload.start_date;
            if (!payload.end_date) delete payload.end_date;
            if (!payload.link) delete payload.link;
            await this.api('/collections/', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            await this.fetchCollections();
            this.showAddCollection = false;
            this.collectionForm = { name: '', description: '', start_date: '', end_date: '', link: '', is_public: false };
            this.showSuccess('Collection created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    viewCollection(collectionId) {
        this.selectedCollection = this.collections.find(c => c.id === collectionId);
        if (this.selectedCollection) {
            this.currentView = 'collection-detail';
        }
    },

    openEditCollection(collection) {
        this.editingCollectionId = collection.id;
        this.collectionForm = {
            name: collection.name,
            description: collection.description || '',
            start_date: collection.start_date || '',
            end_date: collection.end_date || '',
            link: collection.link || '',
            is_public: collection.is_public || false
        };
        this.showEditCollection = true;
    },

    async updateCollection() {
        try {
            const payload = { ...this.collectionForm };
            if (!payload.description) delete payload.description;
            if (!payload.start_date) delete payload.start_date;
            if (!payload.end_date) delete payload.end_date;
            if (!payload.link) delete payload.link;
            
            await this.api(`/collections/${this.editingCollectionId}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            await this.fetchCollections();
            this.showEditCollection = false;
            this.editingCollectionId = null;
            this.collectionForm = { name: '', description: '', start_date: '', end_date: '', link: '', is_public: false };
            this.showSuccess('Collection updated!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteCollection(collectionId) {
        if (!confirm('Delete this collection?')) return;
        this.loading = true;
        try {
            await this.api(`/collections/${collectionId}`, { method: 'DELETE' });
            await this.fetchCollections();
            this.showSuccess('Collection deleted!');
        } catch (err) {
            this.showError(err.message);
        } finally {
            this.loading = false;
        }
    },

    async fetchCategories() {
        const data = await this.api('/categories/');
        // Categories returns array directly (not paginated)
        this.categories = Array.isArray(data) ? data : (data.categories || data);
    },

    async createCategory() {
        try {
            await this.api('/categories/', {
                method: 'POST',
                body: JSON.stringify(this.categoryForm)
            });
            await this.fetchCategories();
            this.showAddCategory = false;
            this.categoryForm = { name: '', icon: '', is_public: false };
            this.showSuccess('Category created!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    openEditCategory(category) {
        this.editingCategoryId = category.id;
        this.categoryForm = {
            name: category.name,
            icon: category.icon || '',
            color: category.color || '',
            is_public: category.is_public || false
        };
        this.showEditCategory = true;
    },

    async updateCategory() {
        try {
            await this.api(`/categories/${this.editingCategoryId}`, {
                method: 'PUT',
                body: JSON.stringify(this.categoryForm)
            });
            await this.fetchCategories();
            this.showEditCategory = false;
            this.editingCategoryId = null;
            this.categoryForm = { name: '', icon: '', color: '', is_public: false };
            this.showSuccess('Category updated!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteCategory(id) {
        if (!confirm('Delete this category?')) return;
        try {
            await this.api(`/categories/${id}`, { method: 'DELETE' });
            await this.fetchCategories();
            this.showSuccess('Category deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async viewLocationFromCollection(locationId) {
        try {
            // Fetch full location data
            const location = await this.api(`/locations/${locationId}`);
            
            // Switch to locations view and set selected location
            this.currentView = 'location-detail';
            this.selectedLocation = location;
            this.locationTab = 'notes';
            
            // Fetch all location sub-resources
            await Promise.all([
                this.fetchLocationNotes(location.id),
                this.fetchLocationVisits(location.id),
                this.fetchLocationActivities(location.id),
                this.fetchLocationChecklists(location.id),
                this.fetchLocationTransportation(location.id),
                this.fetchLocationLodging(location.id),
                this.fetchLocationTrails(location.id)
            ]);
        } catch (err) {
            this.showError(err.message);
        }
    }
};
