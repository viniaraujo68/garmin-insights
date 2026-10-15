<script lang="ts">
  import type { ActivitySummary } from "$lib/data/types";
  import { number } from "$lib/format";
  import { TECHNIQUE, techniqueRank } from "$lib/technique";
  import StatusText from "./StatusText.svelte";

  const { run }: { run: ActivitySummary } = $props();
</script>

<dl class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
  {#each TECHNIQUE as band (band.key)}
    {@const value = run[band.key]}
    {@const rank = techniqueRank(band, value)}
    <div class="flex flex-col gap-0.5">
      <dt class="text-xs text-base-content/70">{band.label}</dt>
      <dd class="text-xl font-semibold tabular-nums">
        {number(value, band.digits)}
        <span class="text-xs font-normal text-base-content/60">{band.unit}</span>
      </dd>
      <dd><StatusText status={rank.status} label={rank.label} /></dd>
      <dd class="text-xs text-base-content/50">{band.help}</dd>
    </div>
  {/each}
</dl>
