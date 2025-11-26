<svelte:options customElement="visit-card" />

<script>
    export let locationname = '';
    export let city = '';
    export let country = '';
    export let startdate = '';
    export let enddate = '';
    export let timezone = '';
    export let notes = '';
    export let showactions = 'true';
    export let showlocation = 'false';
    
    const formatDate = (dateStr) => {
        if (!dateStr) return 'No date';
        return new Date(dateStr + 'T00:00:00').toLocaleDateString();
    };
</script>

<div class="visit-card">
    <div class="visit-header">
        {#if showlocation === 'true' && locationname}
            <div class="location-info">
                <h3>{locationname}</h3>
                {#if city || country}
                    <span class="location-meta">
                        {city}{city && country ? ', ' : ''}{country}
                    </span>
                {/if}
            </div>
        {/if}
    </div>
    
    <div class="visit-content">
        <div class="visit-dates">
            <span class="date-icon">📅</span>
            <span class="date-range">
                {formatDate(startdate)}
                {#if enddate}
                    <span class="arrow">→</span>
                    {formatDate(enddate)}
                {/if}
            </span>
        </div>
        
        {#if timezone}
            <div class="visit-timezone">
                🌍 {timezone}
            </div>
        {/if}
        
        {#if notes}
            <div class="visit-notes">
                {notes}
            </div>
        {/if}
    </div>
    
    {#if showactions === 'true'}
        <div class="visit-actions">
            <button class="btn-delete" on:click={(e) => {
                e.stopPropagation();
                const host = e.target.getRootNode().host;
                if (host) {
                    host.dispatchEvent(new CustomEvent('delete', { bubbles: true, composed: true }));
                }
            }}>
                🗑️
            </button>
        </div>
    {/if}
</div>

<style>
    :host {
        display: block;
        width: 100%;
    }
    
    .visit-card {
        background: var(--card-bg, #fff);
        border: 1px solid var(--border, #e5e7eb);
        border-radius: 0.5rem;
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: start;
        gap: 1rem;
        transition: box-shadow 0.2s;
    }
    
    .visit-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .location-info {
        margin-bottom: 0.75rem;
    }
    
    .location-info h3 {
        margin: 0 0 0.25rem 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text, #1f2937);
    }
    
    .location-meta {
        font-size: 0.875rem;
        color: var(--text-muted, #6b7280);
    }
    
    .visit-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .visit-dates {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9375rem;
    }
    
    .date-icon {
        font-size: 1rem;
    }
    
    .date-range {
        color: var(--text, #1f2937);
    }
    
    .arrow {
        margin: 0 0.25rem;
        color: var(--text-muted, #6b7280);
    }
    
    .visit-timezone {
        font-size: 0.875rem;
        color: var(--text-muted, #6b7280);
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .visit-notes {
        margin-top: 0.25rem;
        padding: 0.75rem;
        background: var(--bg, #f9fafb);
        border-radius: 0.375rem;
        font-size: 0.875rem;
        color: var(--text, #374151);
        white-space: pre-wrap;
        line-height: 1.5;
    }
    
    .visit-actions {
        display: flex;
        align-items: flex-start;
    }
    
    .btn-delete {
        background: transparent;
        border: none;
        font-size: 1.25rem;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        transition: background-color 0.2s;
    }
    
    .btn-delete:hover {
        background: rgba(239, 68, 68, 0.1);
    }
</style>
