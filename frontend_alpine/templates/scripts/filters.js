// Filter, Search, and Pagination Methods
const filterMethods = {
    // Search & Filter
    get filteredLocations() {
        // Ensure locations is an array
        if (!Array.isArray(this.locations)) {
            console.error('locations is not an array:', this.locations);
            return [];
        }
        
        let filtered = this.locations.slice(); // Use slice() instead of spread
        
        // Search
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filtered = filtered.filter(loc => 
                loc.name?.toLowerCase().includes(query) ||
                loc.city?.toLowerCase().includes(query) ||
                loc.country?.toLowerCase().includes(query) ||
                (loc.tags && loc.tags.some(tag => tag.toLowerCase().includes(query)))
            );
        }
        
        // Filter by category
        if (this.filterCategory) {
            filtered = filtered.filter(loc => loc.category?.id === parseInt(this.filterCategory));
        }
        
        // Filter by collection (UUID comparison, not parseInt)
        if (this.filterCollection) {
            filtered = filtered.filter(loc => loc.collection?.id === this.filterCollection);
        }
        
        // Filter by rating
        if (this.filterRating) {
            filtered = filtered.filter(loc => loc.rating === parseInt(this.filterRating));
        }
        
        // Sort
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

    get filteredCollections() {
        if (!this.collectionsSearchQuery) return this.collections;
        const query = this.collectionsSearchQuery.toLowerCase();
        return this.collections.filter(col => 
            col.name?.toLowerCase().includes(query)
        );
    },

    get filteredCategories() {
        if (!this.categoriesSearchQuery) return this.categories;
        const query = this.categoriesSearchQuery.toLowerCase();
        return this.categories.filter(cat => 
            cat.name?.toLowerCase().includes(query) ||
            cat.icon?.toLowerCase().includes(query)
        );
    },

    clearFilters() {
        this.searchQuery = '';
        this.filterCategory = '';
        this.filterCollection = '';
        this.filterRating = '';
        this.sortBy = 'name';
        this.currentPage = 1;
    },

    // Pagination
    get paginatedLocations() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.filteredLocations.slice(start, end);
    },

    get totalPages() {
        return Math.ceil(this.filteredLocations.length / this.itemsPerPage);
    },

    get pageNumbers() {
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

    changePage(page) {
        if (page === '...' || page < 1 || page > this.totalPages) return;
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};
