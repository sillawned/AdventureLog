<svelte:options customElement="transportation-card" />

<script>
    export let type = '';
    export let fromlocation = '';
    export let tolocation = '';
    export let departtime = '';
    export let arrivetime = '';
    export let departtimezone = '';
    export let arrivetimezone = '';
    export let link = '';
    export let rating = '';
    export let showactions = 'true';
    
    const formatDateTime = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleString();
    };
    
    const getTypeEmoji = (transportType) => {
        const emojis = {
            'plane': '✈️',
            'train': '🚂',
            'bus': '🚌',
            'car': '🚗',
            'boat': '🚢',
            'bike': '🚴',
            'walk': '🚶'
        };
        return emojis[transportType?.toLowerCase()] || '🚶';
    };
    
    const renderStars = (count) => {
        return '⭐'.repeat(parseInt(count) || 0);
    };
</script>

<div class="transport-card">
    <div class="transport-content">
        <div class="transport-header">
            <span class="transport-badge">
                {getTypeEmoji(type)} {type}
            </span>
            {#if rating}
                <span class="transport-rating">{renderStars(rating)}</span>
            {/if}
        </div>
        
        <div class="transport-route">
            <span class="route-location">{fromlocation || 'Unknown'}</span>
            <span class="route-arrow">→</span>
            <span class="route-location">{tolocation || 'Unknown'}</span>
        </div>
        
        {#if departtime || arrivetime}
            <div class="transport-times">
                {#if departtime}
                    <span class="time-info">
                        🕒 {formatDateTime(departtime)}
                        {#if departtimezone}
                            <span class="timezone">({departtimezone})</span>
                        {/if}
                    </span>
                {/if}
                {#if arrivetime}
                    <span class="time-arrow">→</span>
                    <span class="time-info">
                        {formatDateTime(arrivetime)}
                        {#if arrivetimezone}
                            <span class="timezone">({arrivetimezone})</span>
                        {/if}
                    </span>
                {/if}
            </div>
        {/if}
        
        {#if link}
            <div class="transport-link">
                🔗 <a href={link} target="_blank" rel="noopener">Details</a>
            </div>
        {/if}
    </div>
    
    {#if showactions === 'true'}
        <div class="transport-actions">
            <button class="btn-delete" on:click={(e) => {
                e.stopPropagation();
                const host = e.target.getRootNode().host;
                if (host) {
                    host.dispatchEvent(new CustomEvent('delete', { bubbles: true, composed: true }));
                }
            }}>
                Delete
            </button>
        </div>
    {/if}
</div>

<style>
    :host {
        display: block;
        width: 100%;
    }
    
    .transport-card {
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
    
    .transport-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .transport-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .transport-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    
    .transport-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: capitalize;
    }
    
    .transport-rating {
        font-size: 0.875rem;
    }
    
    .transport-route {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9375rem;
    }
    
    .route-location {
        color: var(--text, #1f2937);
        font-weight: 500;
    }
    
    .route-arrow {
        color: var(--text-muted, #6b7280);
        font-weight: 600;
    }
    
    .transport-times {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-muted, #6b7280);
    }
    
    .time-info {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .timezone {
        font-size: 0.75rem;
        opacity: 0.8;
    }
    
    .time-arrow {
        font-weight: 600;
    }
    
    .transport-link {
        font-size: 0.875rem;
    }
    
    .transport-link a {
        color: var(--link, #3b82f6);
        text-decoration: none;
    }
    
    .transport-link a:hover {
        text-decoration: underline;
    }
    
    .transport-actions {
        display: flex;
        align-items: flex-start;
    }
    
    .btn-delete {
        background: #ef4444;
        color: white;
        border: none;
        padding: 0.375rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        cursor: pointer;
        transition: background-color 0.2s;
        font-weight: 500;
    }
    
    .btn-delete:hover {
        background: #dc2626;
    }
</style>
