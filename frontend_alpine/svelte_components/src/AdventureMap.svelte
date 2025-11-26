<svelte:options customElement="adventure-map" />

<script>
  import { onMount, onDestroy } from 'svelte';
  import L from 'leaflet';
  
  // Props
  export let locations = '[]'; // Stringified JSON
  export let center = '[20, 0]';
  export let zoom = '2';
  
  let mapElement;
  let map;
  let markers = [];
  let parsedLocations = [];
  let parsedCenter = [20, 0];
  let parsedZoom = 2;
  let checkInterval;
  let checkCount = 0;
  let hasLogged = false;
  
  // Parse props when they change
  $: {
    try {
      parsedLocations = typeof locations === 'string' ? JSON.parse(locations) : locations;
    } catch (e) {
      console.error('Failed to parse locations:', e);
      parsedLocations = [];
    }
  }
  
  $: {
    try {
      parsedCenter = typeof center === 'string' ? JSON.parse(center) : center;
    } catch (e) {
      parsedCenter = [20, 0];
    }
  }
  
  $: {
    try {
      parsedZoom = typeof zoom === 'string' ? parseInt(zoom) : zoom;
    } catch (e) {
      parsedZoom = 2;
    }
  }
  
  function isElementVisible(el) {
    if (!el) return false;
    
    // Check if element or any parent has display: none
    let current = el;
    while (current) {
      const style = window.getComputedStyle(current);
      if (style.display === 'none' || style.visibility === 'hidden') {
        return false;
      }
      current = current.parentElement;
    }
    
    // Check dimensions
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }
  
  function initMap() {
    if (!mapElement || map) return;
    
    if (!isElementVisible(mapElement)) {
      if (!hasLogged) {
        console.log('Waiting for map container to become visible...');
        hasLogged = true;
      }
      return;
    }
    
    // Check if container has actual dimensions (not just visible)
    const rect = mapElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      console.log('Container visible but has no dimensions yet');
      return;
    }
    
    console.log('Container dimensions:', rect.width, 'x', rect.height);
    
    // Check if container already has a map instance
    if (mapElement._leaflet_id) {
      console.warn('Map already initialized on this container');
      return;
    }
    
    console.log('Initializing map...');
    
    try {
      // Initialize Leaflet directly on the element (not by ID)
      // This works in Shadow DOM
      map = L.map(mapElement, {
        fadeAnimation: false,
        zoomAnimation: false
      }).setView(parsedCenter, parsedZoom);
      
      console.log('Map created successfully');
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(map);
      
      updateMarkers();
      
      // Stop checking once map is initialized
      if (checkInterval) {
        clearInterval(checkInterval);
        checkInterval = null;
      }
      
      // Force multiple invalidateSize calls to fix tile positioning
      // This is needed because the container size might not be stable yet
      setTimeout(() => {
        if (map) {
          map.invalidateSize(true);
          console.log('Map size invalidated (100ms)');
        }
      }, 100);
      
      setTimeout(() => {
        if (map) {
          map.invalidateSize(true);
          console.log('Map size invalidated (300ms)');
        }
      }, 300);
      
      setTimeout(() => {
        if (map) {
          map.invalidateSize(true);
          console.log('Map size invalidated (500ms)');
        }
      }, 500);
    } catch (e) {
      console.error('Failed to initialize map:', e);
      // Don't set map variable if initialization failed
      map = null;
    }
  }
  
  onMount(() => {
    console.log('AdventureMap component mounted');
    
    // Wait longer for Alpine.js to fully initialize
    setTimeout(() => {
      console.log('Starting visibility polling...');
      
      // Poll every 200ms to check if element becomes visible
      checkInterval = setInterval(() => {
        if (!map && mapElement) {
          const visible = isElementVisible(mapElement);
          console.log('Checking visibility:', visible, 'Parent display:', mapElement.parentElement ? window.getComputedStyle(mapElement.parentElement).display : 'no parent');
          
          if (visible) {
            initMap();
          }
        }
      }, 200);
      
      // Check if already visible
      if (isElementVisible(mapElement)) {
        console.log('Already visible, initializing...');
        initMap();
      }
    }, 500);
  });
  
  onDestroy(() => {
    if (checkInterval) {
      clearInterval(checkInterval);
    }
    if (map) {
      map.remove();
    }
  });
  
  $: if (map && parsedLocations) {
    updateMarkers();
  }
  
  function updateMarkers() {
    if (!map) return;
    
    // Clear existing markers
    markers.forEach(marker => marker.remove());
    markers = [];
    
    // Add new markers
    parsedLocations.forEach(location => {
      if (location.latitude && location.longitude) {
        const color = location.is_visited ? '#f87171' : '#60a5fa';
        const icon = L.divIcon({
          html: `<div style="background: ${color}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${location.category?.icon || '📍'}</div>`,
          className: 'custom-marker',
          iconSize: [32, 32]
        });
        
        const marker = L.marker([location.latitude, location.longitude], { icon })
          .addTo(map);
        
        // Create popup
        const statusColor = location.is_visited ? '#10b981' : '#3b82f6';
        const statusText = location.is_visited ? 'Visited' : 'Planned';
        
        marker.bindPopup(`
          <div style="min-width: 200px;">
            <h3 style="font-weight: bold; margin-bottom: 8px;">${location.name}</h3>
            <div style="margin-bottom: 8px;">
              <span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                ${statusText}
              </span>
              ${location.category ? `
                <span style="border: 1px solid #e5e7eb; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 4px;">
                  ${location.category.icon} ${location.category.display_name || location.category.name}
                </span>
              ` : ''}
            </div>
            ${location.city || location.country ? `
              <p style="font-size: 12px; color: #666; margin: 4px 0;">
                ${[location.city, location.country].filter(Boolean).join(', ')}
              </p>
            ` : ''}
            <button 
              onclick="window.dispatchEvent(new CustomEvent('location-selected', { detail: '${location.id}' }))"
              style="background: #3b82f6; color: white; padding: 6px 12px; border-radius: 4px; border: none; cursor: pointer; font-size: 14px; width: 100%; margin-top: 8px;">
              View Details
            </button>
          </div>
        `);
        
        markers.push(marker);
      }
    });
    
    // Fit bounds if there are markers
    if (markers.length > 0) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }
  }
</script>

<div bind:this={mapElement} style="width: 100%; height: 100%;"></div>

<style>
  /* Inline critical Leaflet CSS for Shadow DOM compatibility */
  :global(.leaflet-pane),
  :global(.leaflet-tile),
  :global(.leaflet-marker-icon),
  :global(.leaflet-marker-shadow),
  :global(.leaflet-tile-container),
  :global(.leaflet-pane) > :global(svg),
  :global(.leaflet-pane) > :global(canvas),
  :global(.leaflet-zoom-box),
  :global(.leaflet-image-layer),
  :global(.leaflet-layer) {
    position: absolute;
    left: 0;
    top: 0;
  }
  
  :global(.leaflet-container) {
    overflow: hidden;
  }
  
  :global(.leaflet-tile),
  :global(.leaflet-marker-icon),
  :global(.leaflet-marker-shadow) {
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
    -webkit-user-drag: none;
  }
  
  :global(.leaflet-tile::selection) {
    background: transparent;
  }
  
  :global(.leaflet-safari) :global(.leaflet-tile) {
    image-rendering: -webkit-optimize-contrast;
  }
  
  :global(.leaflet-safari) :global(.leaflet-tile-container) {
    width: 1600px;
    height: 1600px;
    -webkit-transform-origin: 0 0;
  }
  
  :global(.leaflet-marker-icon),
  :global(.leaflet-marker-shadow) {
    display: block;
  }
  
  :global(.leaflet-container) :global(.leaflet-overlay-pane) :global(svg) {
    -moz-user-select: none;
  }
  
  :global(.leaflet-pane) { z-index: 400; }
  :global(.leaflet-tile-pane) { z-index: 200; }
  :global(.leaflet-overlay-pane) { z-index: 400; }
  :global(.leaflet-shadow-pane) { z-index: 500; }
  :global(.leaflet-marker-pane) { z-index: 600; }
  :global(.leaflet-tooltip-pane) { z-index: 650; }
  :global(.leaflet-popup-pane) { z-index: 700; }
  
  :global(.leaflet-map-pane) :global(canvas) { z-index: 100; }
  :global(.leaflet-map-pane) :global(svg) { z-index: 200; }
  
  :global(.leaflet-vml-shape) {
    width: 1px;
    height: 1px;
  }
  
  :global(.lvml) {
    behavior: url(#default#VML);
    display: inline-block;
    position: absolute;
  }
  
  :global(.leaflet-control) {
    position: relative;
    z-index: 800;
    pointer-events: visiblePainted;
    pointer-events: auto;
  }
  
  :global(.leaflet-top),
  :global(.leaflet-bottom) {
    position: absolute;
    z-index: 1000;
    pointer-events: none;
  }
  
  :global(.leaflet-top) {
    top: 0;
  }
  
  :global(.leaflet-right) {
    right: 0;
  }
  
  :global(.leaflet-bottom) {
    bottom: 0;
  }
  
  :global(.leaflet-left) {
    left: 0;
  }
  
  :global(.leaflet-control) {
    float: left;
    clear: both;
  }
  
  :global(.leaflet-right) :global(.leaflet-control) {
    float: right;
  }
  
  :global(.leaflet-top) :global(.leaflet-control) {
    margin-top: 10px;
  }
  
  :global(.leaflet-bottom) :global(.leaflet-control) {
    margin-bottom: 10px;
  }
  
  :global(.leaflet-left) :global(.leaflet-control) {
    margin-left: 10px;
  }
  
  :global(.leaflet-right) :global(.leaflet-control) {
    margin-right: 10px;
  }

  :host {
    display: block;
    width: 100%;
    height: 100%;
  }
</style>
