<svelte:options customElement="note-card" />

<script>
    export let title = '';
    export let content = '';
    export let showactions = 'true';
    
    function handleDelete(e) {
        e.stopPropagation();
        const host = e.target.getRootNode().host;
        if (host) {
            host.dispatchEvent(new CustomEvent('delete', { bubbles: true, composed: true }));
        }
    }
</script>

<div class="note-card">
    <div class="note-content">
        <h4 class="note-title">{title}</h4>
        <p class="note-text">{content}</p>
    </div>
    
    {#if showactions === 'true'}
        <div class="note-actions">
            <button class="btn-delete" on:click={handleDelete}>
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
    
    .note-card {
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
    
    .note-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .note-content {
        flex: 1;
    }
    
    .note-title {
        margin: 0 0 0.5rem 0;
        font-size: 1.0625rem;
        font-weight: 600;
        color: var(--text, #1f2937);
    }
    
    .note-text {
        margin: 0;
        font-size: 0.9375rem;
        color: var(--text, #374151);
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    .note-actions {
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
