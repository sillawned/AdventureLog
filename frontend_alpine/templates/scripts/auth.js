// Authentication Methods
const authMethods = {
    async login() {
        this.loading = true;
        try {
            // OAuth2 expects form-urlencoded data
            const formData = new URLSearchParams();
            formData.append('username', this.loginForm.username);
            formData.append('password', this.loginForm.password);
            
            const res = await fetch(`${API_URL}/auth/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                this.token = data.access_token;
                localStorage.setItem('token', data.access_token);
                await this.fetchUser();
                this.currentView = 'dashboard';
                await Promise.all([
                    this.fetchStats(),
                    this.fetchLocations(),
                    this.fetchCollections(),
                    this.fetchCategories(),
                    this.fetchAllVisits()
                ]);
                this.loginForm = { username: '', password: '' };
            } else {
                this.showError(data.detail || 'Login failed');
            }
        } catch (err) {
            this.showError('Login failed: ' + err.message);
        } finally {
            this.loading = false;
        }
    },

    async register() {
        this.loading = true;
        try {
            const res = await fetch(`${API_URL}/auth/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.registerForm)
            });
            const data = await res.json();
            if (res.ok) {
                this.showSuccess('Registration successful! Please login.');
                this.currentView = 'login';
                this.registerForm = { username: '', email: '', password: '' };
            } else {
                this.showError(data.username?.[0] || data.email?.[0] || 'Registration failed');
            }
        } catch (err) {
            this.showError('Registration failed');
        } finally {
            this.loading = false;
        }
    },

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        this.currentView = 'home';
        this.locations = [];
        this.collections = [];
        this.categories = [];
    },

    async fetchUser() {
        const data = await this.api('/auth/me');
        this.user = data;
    }
};
