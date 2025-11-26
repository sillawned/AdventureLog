<svelte:options customElement="category-card" />

<script>
  export let name = '';
  export let icon = '📁';
  export let ispublic = 'false';
  export let showactions = 'false';

  $: isPublic = String(ispublic) === 'true';

  function handleDelete(e) {
    e.stopPropagation();
    const host = e.target.getRootNode().host;
    if (host) {
      host.dispatchEvent(new CustomEvent('delete', { bubbles: true, composed: true }));
    }
  }
</script>

<div class="card">
  <div class="card-body">
    <div class="header">
      <div class="left">
        <span class="icon">{icon}</span>
        <h3>{name}</h3>
      </div>
      {#if showactions === 'true'}
        <button class="btn-icon btn-danger" on:click|stopPropagation={handleDelete}>🗑️</button>
      {/if}
    </div>
    <div class="badges">
      <span class="badge" class:badge-public={isPublic} class:badge-private={!isPublic}>{isPublic ? 'Public' : 'Private'}</span>
    </div>
  </div>
</div>

<style>
  :host { display: block; height: 100%; min-height: 90px; }
  .card { background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.08); height: 100%; display: flex; }
  .card-body { padding: 16px; width: 100%; }
  .header { display: flex; justify-content: space-between; align-items: center; }
  .left { display: flex; align-items: center; gap: 8px; }
  .icon { font-size: 1.5rem; }
  h3 { margin: 0; font-size: 1rem; color: #111827; }
  .badges { margin-top: 8px; }
  .badge { padding: 4px 10px; border-radius: 12px; font-size: .8rem; background: #f3f4f6; color: #374151; }
  .badge-public { background: #dcfce7; color: #166534; }
  .badge-private { background: #fee2e2; color: #991b1b; }
  .btn-icon { background: transparent; border: 1px solid #ef4444; color: #ef4444; border-radius: 8px; padding: 4px 8px; cursor: pointer; }
  .btn-icon:hover { background: #fef2f2; }
</style>
