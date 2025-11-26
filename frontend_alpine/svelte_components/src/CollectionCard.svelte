<svelte:options customElement="collection-card" />

<script>
  export let name = '';
  export let description = '';
  export let startdate = '';
  export let enddate = '';
  export let link = '';
  export let locationscount = '0';
  export let showactions = 'false';

  $: count = parseInt(locationscount) || 0;

  function handleDelete(e) {
    e.stopPropagation();
    const host = e.target.getRootNode().host;
    if (host) {
      host.dispatchEvent(new CustomEvent('delete', { bubbles: true, composed: true }));
    }
  }

  function handleView(e) {
    e.stopPropagation();
    const host = e.target.getRootNode().host;
    if (host) {
      host.dispatchEvent(new CustomEvent('view', { bubbles: true, composed: true }));
    }
  }
</script>

<div class="card">
  <div class="card-body">
    <div class="header">
      <div class="title">
        <h4>{name}</h4>
        {#if description}
          <p class="desc">{description}</p>
        {/if}
      </div>
      {#if showactions === 'true'}
        <div class="actions">
          <button class="btn btn-outline btn-sm" on:click|stopPropagation={handleView}>View</button>
          <button class="btn btn-danger btn-sm" on:click|stopPropagation={handleDelete}>Delete</button>
        </div>
      {/if}
    </div>

    {#if startdate || enddate}
      <p class="dates text-muted">
        {#if startdate}{new Date(startdate).toLocaleDateString()}{/if}
        {#if enddate} → {new Date(enddate).toLocaleDateString()}{/if}
      </p>
    {/if}

    {#if link}
      <p class="link"><span class="emoji">🔗</span> <a href={link} target="_blank" rel="noopener">Link</a></p>
    {/if}

    <p class="count text-muted">{count} {count === 1 ? 'location' : 'locations'}</p>
  </div>
</div>

<style>
  :host { display: block; height: 100%; min-height: 120px; }
  .card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.08); height: 100%; display: flex; }
  .card-body { padding: 16px; display: flex; flex-direction: column; gap: 8px; width: 100%; }
  .header { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
  .title h4 { margin: 0; font-size: 1rem; line-height: 1.3; color: #111827; }
  .desc { margin: 4px 0 0; font-size: .9rem; color: #6b7280; }
  .dates { font-size: .8rem; color: #6b7280; }
  .link { font-size: .85rem; }
  .link a { color: #2563eb; text-decoration: underline; }
  .emoji { margin-right: 6px; }
  .count { font-size: .9rem; color: #6b7280; margin-top: auto; }
  .actions { display: flex; gap: 8px; }
  .btn { padding: 4px 10px; border-radius: 6px; border: 1px solid #d1d5db; background: #fff; cursor: pointer; font-size: .85rem; }
  .btn:hover { background: #f3f4f6; }
  .btn-danger { border-color: #ef4444; color: #ef4444; }
  .btn-danger:hover { background: #fef2f2; }
  .btn-outline { border-color: #3b82f6; color: #3b82f6; }
  .btn-outline:hover { background: #eff6ff; }
</style>
