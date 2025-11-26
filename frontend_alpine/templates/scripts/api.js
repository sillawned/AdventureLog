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
        
        // Handle 204 No Content responses (common for DELETE)
        if (res.status === 204 || res.headers.get('content-length') === '0') {
            return null;
        }
        
        // Check if there's actually JSON to parse
        const contentType = res.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return res.json();
        }
        
        return null;
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
