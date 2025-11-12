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

    async deleteCollection(id) {
        if (!confirm('Delete this collection?')) return;
        try {
            await this.api(`/collections/${id}`, { method: 'DELETE' });
            await this.fetchCollections();
            this.showSuccess('Collection deleted!');
        } catch (err) {
            this.showError(err.message);
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

    async deleteCategory(id) {
        if (!confirm('Delete this category?')) return;
        try {
            await this.api(`/categories/${id}`, { method: 'DELETE' });
            await this.fetchCategories();
            this.showSuccess('Category deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    }
};
