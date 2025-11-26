<svelte:options customElement="location-card" />

<script>
    export let name = '';
    export let city = '';
    export let country = '';
    export let location = '';
    export let image = '';
    export let rating = 0;
    export let category = '';
    export let categorycolor = '';
    export let collection = '';
    export let tags = '';
    export let activitytype = '';
    export let variant = 'default'; // 'default', 'compact', 'profile'
    export let showactions = 'false';
    
    let parsedTags = [];
    
    $: {
        try {
            parsedTags = tags ? JSON.parse(tags) : [];
        } catch (e) {
            parsedTags = [];
        }
    }
    
    $: parsedRating = parseInt(rating) || 0;
    
    function handleView(e) {
        e.stopPropagation();
        const host = e.target.getRootNode().host;
        if (host) {
            host.dispatchEvent(new CustomEvent('view', {
                detail: { name, city, country, location },
                bubbles: true,
                composed: true
            }));
        }
    }
    
    function handleDelete(e) {
        e.stopPropagation();
        const host = e.target.getRootNode().host;
        if (host) {
            host.dispatchEvent(new CustomEvent('delete', {
                detail: { name },
                bubbles: true,
                composed: true
            }));
        }
    }
</script>

<style>
    :host {
        display: block;
        height: 100%;
        min-height: 200px;
    }
    
    .location-card {
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        overflow: hidden;
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .location-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .location-card.clickable {
        cursor: pointer;
    }
    
    .location-card.clickable:hover {
        transform: translateY(-2px);
    }
    
    .card-image {
        width: 100%;
        height: 192px;
        object-fit: cover;
        background: #f3f4f6;
    }
    
    .card-body {
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 12px;
        gap: 12px;
    }
    
    .card-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 4px 0;
        color: #1f2937;
        line-height: 1.3;
    }
    
    .card-location {
        font-size: 14px;
        color: #6b7280;
        margin: 0;
    }
    
    .card-actions {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }
    
    .btn {
        padding: 4px 12px;
        font-size: 14px;
        border-radius: 6px;
        border: 1px solid #d1d5db;
        background: #fff;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .btn:hover {
        background: #f3f4f6;
    }
    
    .btn-view {
        color: #3b82f6;
        border-color: #3b82f6;
    }
    
    .btn-view:hover {
        background: #eff6ff;
    }
    
    .btn-delete {
        color: #ef4444;
        border-color: #ef4444;
    }
    
    .btn-delete:hover {
        background: #fef2f2;
    }
    
    .card-meta {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: auto;
    }
    
    .badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .badge {
        padding: 4px 10px;
        font-size: 12px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-category {
        color: #fff;
        background: var(--category-color, #6b7280);
    }
    
    .badge-collection {
        color: #fff;
        background: #8b5cf6;
    }
    
    .badge-activity {
        color: #3b82f6;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
    }
    
    .badge-tag {
        color: #6b7280;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
    }
    
    .rating {
        font-size: 14px;
        line-height: 1;
        color: #fbbf24;
    }
    
    .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
    }
    
    /* Compact variant */
    .location-card.compact .card-body {
        padding: 12px;
    }
    
    .location-card.compact .card-title {
        font-size: 16px;
    }
    
    .location-card.compact .card-image {
        height: 128px;
    }
    
    /* Profile variant */
    .location-card.profile {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .location-card.profile:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
</style>

<div 
    class="location-card {variant} {variant === 'profile' ? 'clickable' : ''}"
    on:click={variant === 'profile' ? handleView : null}
>
    {#if image}
        <img src={image} alt={name} class="card-image" />
    {/if}
    
    <div class="card-body">
        <div class="card-header">
            <div>
                <h4 class="card-title">{name}</h4>
                {#if variant === 'profile' && location}
                    <p class="card-location">{location}</p>
                {:else if city || country}
                    <p class="card-location">
                        {#if city}{city}{/if}{#if city && country}, {/if}{#if country}{country}{/if}
                    </p>
                {/if}
            </div>
            
            {#if showactions === 'true'}
                <div class="card-actions">
                    <button class="btn btn-view" on:click|stopPropagation={handleView}>View</button>
                    <button class="btn btn-delete" on:click|stopPropagation={handleDelete}>Delete</button>
                </div>
            {/if}
        </div>
        
        <div class="card-meta">
            {#if category || collection || activitytype}
                <div class="badges">
                    {#if category}
                        <span 
                            class="badge badge-category" 
                            style="--category-color: {categorycolor || '#6b7280'}"
                        >
                            {category}
                        </span>
                    {/if}
                    {#if collection}
                        <span class="badge badge-collection">{collection}</span>
                    {/if}
                    {#if activitytype}
                        <span class="badge badge-activity">{activitytype}</span>
                    {/if}
                </div>
            {/if}
            
            {#if parsedRating > 0}
                <div class="rating">
                    {'⭐'.repeat(parsedRating)}
                </div>
            {/if}
            
            {#if parsedTags.length > 0}
                <div class="tags">
                    {#each parsedTags as tag}
                        <span class="badge badge-tag">{tag}</span>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>
