// API Helper Methods
const apiMethods = {
    async api(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
        };
        
        const res = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: { ...headers, ...options.headers }
        });
        
        if (!res.ok) {
            let errorMessage = 'Request failed';
            try {
                const errorData = await res.json();
                if (Array.isArray(errorData)) {
                    errorMessage = errorData.map(err => err.msg || JSON.stringify(err)).join(', ');
                } else if (typeof errorData === 'object') {
                    errorMessage = errorData.detail || errorData.message || Object.values(errorData).flat().join(', ') || 'Request failed';
                } else if (typeof errorData === 'string') {
                    errorMessage = errorData;
                }
            } catch (e) {
                errorMessage = `Request failed with status ${res.status}`;
            }
            throw new Error(errorMessage);
        }
        
        return res.json();
    },

    showError(message) {
        this.error = message;
        setTimeout(() => this.error = '', 5000);
    },

    showSuccess(message) {
        this.success = message;
        setTimeout(() => this.success = '', 3000);
    }
};
