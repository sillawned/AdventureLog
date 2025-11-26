<svelte:options customElement="stats-card" />

<script>
  export let label = '';
  export let value = '0';
  export let variant = 'default'; // default, success, error, warning, info
  export let icon = '';
  export let size = 'medium'; // small, medium, large
</script>

<div class="stat-card stat-{variant} stat-{size}">
  {#if icon}
    <div class="stat-icon">{icon}</div>
  {/if}
  <div class="stat-content">
    <div class="stat-value">{value}</div>
    <div class="stat-label">{label}</div>
  </div>
</div>

<style>
    :host {
        display: block;
        height: 100%;
        min-height: 80px;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 16px;
        height: 100%;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .stat-icon {
        font-size: 32px;
        line-height: 1;
        flex-shrink: 0;
    }

    .stat-content {
        flex: 1;
        min-width: 0;
    }

    .stat-value {
        font-size: 28px;
        font-weight: bold;
        line-height: 1.2;
        margin-bottom: 4px;
    }

    .stat-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
    }

    /* Size variants */
    .stat-small {
        padding: 12px 16px;
    }

    .stat-small .stat-icon {
        font-size: 24px;
    }

    .stat-small .stat-value {
        font-size: 20px;
    }

    .stat-small .stat-label {
        font-size: 12px;
    }

    .stat-large {
        padding: 28px 32px;
    }

    .stat-large .stat-icon {
        font-size: 40px;
    }

    .stat-large .stat-value {
        font-size: 36px;
    }

    .stat-large .stat-label {
        font-size: 16px;
    }

    /* Color variants */
    .stat-success {
        border-left: 4px solid #10b981;
    }

    .stat-success .stat-value {
        color: #10b981;
    }

    .stat-error {
        border-left: 4px solid #ef4444;
    }

    .stat-error .stat-value {
        color: #ef4444;
    }

    .stat-warning {
        border-left: 4px solid #f59e0b;
    }

    .stat-warning .stat-value {
        color: #f59e0b;
    }

    .stat-info {
        border-left: 4px solid #3b82f6;
    }

    .stat-info .stat-value {
        color: #3b82f6;
    }

    .stat-default {
        border-left: 4px solid #6b7280;
    }

    .stat-default .stat-value {
        color: #1f2937;
    }
</style>
