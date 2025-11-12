// Stats and Visits Methods
const statsMethods = {
    async fetchStats() {
        this.stats = await this.api('/stats/');
    },

    async fetchAllVisits() {
        const data = await this.api('/visits/');
        this.allVisits = data.visits || [];
    }
};
