// Export all Svelte components as web components
import AdventureMap from './AdventureMap.svelte';
import StatsCard from './StatsCard.svelte';
import LocationCard from './LocationCard.svelte';
import CountryCard from './CountryCard.svelte';
import CollectionCard from './CollectionCard.svelte';
import CategoryCard from './CategoryCard.svelte';
import VisitCard from './VisitCard.svelte';
import NoteCard from './NoteCard.svelte';
import ActivityCard from './ActivityCard.svelte';
import TransportationCard from './TransportationCard.svelte';
// import AdventureCalendar from './AdventureCalendar.svelte';

// They will be automatically registered as custom elements
// due to the customElement option in svelte config
export { 
    AdventureMap, 
    StatsCard, 
    LocationCard, 
    CountryCard, 
    CollectionCard, 
    CategoryCard,
    VisitCard,
    NoteCard,
    ActivityCard,
    TransportationCard
};
