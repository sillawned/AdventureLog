// Additional features JavaScript methods

// Search functionality
window.performSearch = async function() {
    if (!this.searchQuery || this.searchQuery.trim() === '') {
        this.searchResults = null;
        this.searchResultsCount = 0;
        return;
    }

    try {
        const response = await fetch(`${this.apiUrl}/search/?query=${encodeURIComponent(this.searchQuery)}`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            this.searchResults = data;
            this.searchResultsCount = (data.locations?.length || 0) +
                                      (data.collections?.length || 0) +
                                      (data.countries?.length || 0) +
                                      (data.regions?.length || 0) +
                                      (data.cities?.length || 0) +
                                      (data.users?.length || 0);
        }
    } catch (error) {
        console.error('Search error:', error);
        this.showAlert('Search failed', 'error');
    }
};

// Calendar functionality
window.loadCalendarEvents = async function() {
    try {
        const response = await fetch(`${this.apiUrl}/adventures/calendar/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            this.calendarEvents = data.events || [];
            this.generateCalendarDays();
        }
    } catch (error) {
        console.error('Calendar load error:', error);
    }
};

window.generateCalendarDays = function() {
    const year = this.calendarCurrentDate.getFullYear();
    const month = this.calendarCurrentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const currentDate = new Date(startDate);
    
    while (days.length < 42) {
        const dayEvents = (this.calendarEvents || []).filter(event => {
            const eventDate = new Date(event.start);
            return eventDate.getDate() === currentDate.getDate() &&
                   eventDate.getMonth() === currentDate.getMonth() &&
                   eventDate.getFullYear() === currentDate.getFullYear();
        });
        
        days.push({
            date: new Date(currentDate),
            dayNumber: currentDate.getDate(),
            isCurrentMonth: currentDate.getMonth() === month,
            isToday: this.isToday(currentDate),
            events: dayEvents
        });
        
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    this.calendarDays = days;
};

window.previousMonth = function() {
    this.calendarCurrentDate.setMonth(this.calendarCurrentDate.getMonth() - 1);
    this.calendarCurrentDate = new Date(this.calendarCurrentDate);
    this.generateCalendarDays();
};

window.nextMonth = function() {
    this.calendarCurrentDate.setMonth(this.calendarCurrentDate.getMonth() + 1);
    this.calendarCurrentDate = new Date(this.calendarCurrentDate);
    this.generateCalendarDays();
};

window.goToToday = function() {
    this.calendarCurrentDate = new Date();
    this.generateCalendarDays();
};

window.isToday = function(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
};

window.viewEventDetail = function(event) {
    this.selectedCalendarEvent = event;
};

window.formatEventDate = function(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

window.downloadICS = async function() {
    try {
        const response = await fetch(`${this.apiUrl}/adventures/calendar/download/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'adventures.ics';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            this.showAlert('Calendar downloaded successfully', 'success');
        }
    } catch (error) {
        console.error('ICS download error:', error);
        this.showAlert('Failed to download calendar', 'error');
    }
};

// Settings functionality
window.updateProfile = async function() {
    try {
        const response = await fetch(`${this.apiUrl}/auth/user/`, {
            method: 'PATCH',
            headers: {
                ...this.getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: this.currentUser.username,
                email: this.currentUser.email,
                first_name: this.currentUser.first_name,
                last_name: this.currentUser.last_name,
                public_profile: this.currentUser.public_profile
            })
        });

        if (response.ok) {
            this.showAlert('Profile updated successfully', 'success');
            await this.fetchUserData();
        } else {
            this.showAlert('Failed to update profile', 'error');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        this.showAlert('Failed to update profile', 'error');
    }
};

window.savePreferences = function() {
    localStorage.setItem('measurementSystem', this.useImperialSystem ? 'imperial' : 'metric');
    localStorage.setItem('theme', this.selectedTheme);
    this.showAlert('Preferences saved', 'success');
};

window.changeTheme = function() {
    // Implement theme changing logic
    document.documentElement.setAttribute('data-theme', this.selectedTheme === 'auto' ? 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : 
        this.selectedTheme
    );
};

window.exportData = async function() {
    try {
        const response = await fetch(`${this.apiUrl}/export/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `adventurelog-export-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            this.showAlert('Data exported successfully', 'success');
        }
    } catch (error) {
        console.error('Export error:', error);
        this.showAlert('Failed to export data', 'error');
    }
};

window.confirmDeleteAccount = function() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        this.deleteAccount();
    }
};

window.deleteAccount = async function() {
    try {
        const response = await fetch(`${this.apiUrl}/auth/user/`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            this.showAlert('Account deleted', 'success');
            this.logout();
        } else {
            this.showAlert('Failed to delete account', 'error');
        }
    } catch (error) {
        console.error('Delete account error:', error);
        this.showAlert('Failed to delete account', 'error');
    }
};

// Profile functionality
window.loadProfile = async function(userId) {
    try {
        const response = await fetch(`${this.apiUrl}/users/${userId}/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            this.profileUser = await response.json();
            await this.loadProfileStats(userId);
            await this.loadProfileLocations(userId);
            await this.loadProfileCollections(userId);
        }
    } catch (error) {
        console.error('Profile load error:', error);
    }
};

window.loadProfileStats = async function(userId) {
    try {
        const response = await fetch(`${this.apiUrl}/users/${userId}/stats/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            this.profileStats = await response.json();
        }
    } catch (error) {
        console.error('Profile stats load error:', error);
    }
};

window.loadProfileLocations = async function(userId) {
    try {
        const response = await fetch(`${this.apiUrl}/users/${userId}/locations/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            this.profileLocations = await response.json();
        }
    } catch (error) {
        console.error('Profile locations load error:', error);
    }
};

window.loadProfileCollections = async function(userId) {
    try {
        const response = await fetch(`${this.apiUrl}/users/${userId}/collections/`, {
            headers: this.getAuthHeaders()
        });

        if (response.ok) {
            this.profileCollections = await response.json();
        }
    } catch (error) {
        console.error('Profile collections load error:', error);
    }
};

window.viewProfile = function(userId) {
    this.currentView = 'profile';
    this.loadProfile(userId);
};

window.viewCountry = function(countryId) {
    this.currentView = 'worldtravel';
    this.selectedCountry = countryId;
    this.loadWorldTravel();
};

window.viewRegion = function(countryId, regionId) {
    this.currentView = 'worldtravel';
    this.selectedCountry = countryId;
    this.selectedRegion = regionId;
    this.loadWorldTravel();
};
