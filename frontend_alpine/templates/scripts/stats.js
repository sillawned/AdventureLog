// Stats and Visits Methods
const statsMethods = {
    async fetchStats() {
        this.stats = await this.api('/stats/');
    },

    async fetchAllVisits() {
        const data = await this.api('/visits/');
        this.allVisits = data.visits || [];
    },

    openEditVisit(visit) {
        this.editingVisitId = visit.id;
        this.visitForm = {
            start_date: visit.start_date || '',
            end_date: visit.end_date || '',
            timezone: visit.timezone || '',
            notes: visit.notes || ''
        };
        this.showEditVisit = true;
    },

    async updateVisit() {
        try {
            const payload = { ...this.visitForm };
            if (!payload.end_date) delete payload.end_date;
            if (!payload.timezone) delete payload.timezone;
            if (!payload.notes) delete payload.notes;
            
            await this.api(`/visits/${this.editingVisitId}`, {
                method: 'PATCH',
                body: JSON.stringify(payload)
            });
            await Promise.all([
                this.fetchAllVisits(),
                this.fetchStats()
            ]);
            this.showEditVisit = false;
            this.editingVisitId = null;
            this.visitForm = { start_date: '', end_date: '', timezone: '', notes: '' };
            this.showSuccess('Visit updated!');
        } catch (err) {
            this.showError(err.message);
        }
    },

    async deleteVisit(visitId) {
        if (!confirm('Delete this visit?')) return;
        try {
            await this.api(`/visits/${visitId}`, { method: 'DELETE' });
            await Promise.all([
                this.fetchAllVisits(),
                this.fetchStats()
            ]);
            this.showSuccess('Visit deleted!');
        } catch (err) {
            this.showError(err.message);
        }
    }
};
