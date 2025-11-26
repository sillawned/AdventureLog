<svelte:options customElement="adventure-calendar" />

<script>
  import { onMount } from 'svelte';
  import Calendar from '@event-calendar/core';
  import TimeGrid from '@event-calendar/time-grid';
  import DayGrid from '@event-calendar/day-grid';
  import Interaction from '@event-calendar/interaction';
  
  export let events = [];
  
  let calendarElement;
  let calendar;
  
  onMount(() => {
    calendar = new Calendar({
      target: calendarElement,
      props: {
        plugins: [TimeGrid, DayGrid, Interaction],
        options: {
          view: 'dayGridMonth',
          events: events || [],
          headerToolbar: {
            start: 'prev,next today',
            center: 'title',
            end: 'dayGridMonth,timeGridWeek,timeGridDay'
          }
        }
      }
    });
    
    return () => {
      if (calendar) calendar.$destroy();
    };
  });
  
  $: if (calendar && events) {
    calendar.setOption('events', events);
  }
</script>

<div bind:this={calendarElement}></div>

<style>
  :host {
    display: block;
    width: 100%;
  }
</style>
