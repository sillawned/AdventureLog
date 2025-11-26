<svelte:options customElement="activity-card" />

<script>
    export let type = '';
    export let date = '';
    export let showactions = 'true';
    
    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString();
    };
</script>

<div class="activity-card">
    <div class="activity-content">
        <h4 class="activity-type">{type}</h4>
        {#if date}
            <p class="activity-date">{formatDate(date)}</p>
        {/if}
    </div>
    
    {#if showactions === 'true'}
        <div class="activity-actions">
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
    
    .activity-card {
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
    
    .activity-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .activity-content {
        flex: 1;
    }
    
    .activity-type {
        margin: 0 0 0.25rem 0;
        font-size: 1.0625rem;
        font-weight: 600;
        color: var(--text, #1f2937);
    }
    
    .activity-date {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-muted, #6b7280);
    }
    
    .activity-actions {
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
