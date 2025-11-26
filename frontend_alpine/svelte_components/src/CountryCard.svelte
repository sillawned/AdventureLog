<svelte:options customElement="country-card" />

<script>
    export let name = '';
    export let countrycode = '';
    export let capital = '';
    export let numregions = '0';
    export let numvisits = '0';
    
    $: regions = parseInt(numregions) || 0;
    $: visits = parseInt(numvisits) || 0;
    $: progress = regions > 0 ? (visits / regions * 100) : 0;
    $: isComplete = visits === regions && regions > 0;
    
    function handleClick(e) {
        e.stopPropagation();
        const host = e.target.getRootNode().host;
        if (host) {
            host.dispatchEvent(new CustomEvent('cardclick', {
                detail: { name, countrycode, capital },
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
    }
    
    .country-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .country-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .country-flag {
        width: 100%;
        height: 80px;
        border-radius: 8px;
        overflow: hidden;
        background: #f3f4f6;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .country-flag img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .country-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .country-name {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
        color: #1f2937;
        line-height: 1.3;
    }
    
    .country-meta {
        font-size: 14px;
        color: #6b7280;
        margin: 0;
    }
    
    .country-stats {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
    }
    
    .stat-badge {
        padding: 4px 10px;
        font-size: 12px;
        border-radius: 12px;
        font-weight: 500;
        background: #f3f4f6;
        color: #6b7280;
        white-space: nowrap;
    }
    
    .stat-badge.stat-visited {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .stat-badge.stat-complete {
        background: #dcfce7;
        color: #166534;
    }
    
    .country-progress {
        width: 100%;
        height: 6px;
        background: #e5e7eb;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 4px;
    }
    
    .country-progress-bar {
        height: 100%;
        background: #3b82f6;
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .country-progress-bar.complete {
        background: #10b981;
    }
</style>

<div class="country-card" on:click={handleClick}>
    {#if countrycode}
        <div class="country-flag">
            <img 
                src="https://flagpedia.net/data/flags/w580/{countrycode.toLowerCase()}.webp" 
                alt="{name} flag"
                on:error={(e) => e.target.style.display = 'none'}
            />
        </div>
    {/if}
    
    <div class="country-info">
        <h3 class="country-name">{name}</h3>
        <p class="country-meta">
            {countrycode}
            {#if capital}
                • {capital}
            {/if}
        </p>
        
        <div class="country-stats">
            <span class="stat-badge">{regions} regions</span>
            {#if visits > 0}
                <span class="stat-badge stat-visited">{visits} visited</span>
            {/if}
            {#if isComplete}
                <span class="stat-badge stat-complete">✓ Complete</span>
            {/if}
        </div>
        
        {#if regions > 0}
            <div class="country-progress">
                <div 
                    class="country-progress-bar" 
                    class:complete={isComplete}
                    style="width: {progress}%"
                ></div>
            </div>
        {/if}
    </div>
</div>
