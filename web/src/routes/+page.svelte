<script lang="ts">
  import DayView from "$lib/components/DayView.svelte";

  const { data } = $props();
</script>

<DayView {data} />
