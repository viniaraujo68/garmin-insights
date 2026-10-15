<script lang="ts">
  import type { BaselineTile } from "$lib/data/types";
  import Sparkline from "./Sparkline.svelte";
  import StatusText from "./StatusText.svelte";

  const { tile }: { tile: BaselineTile } = $props();
</script>

<article class="card border border-base-content/10 bg-base-100">
  <div class="card-body gap-1 p-4">
    <h3 class="text-xs font-medium tracking-wide text-base-content/70 uppercase">{tile.label}</h3>
    <div class="flex items-baseline justify-between gap-2">
      <span class="text-2xl font-semibold tracking-tight tabular-nums">{tile.display}</span>
      <span class="text-sm text-base-content/70 tabular-nums">{tile.delta_display}</span>
    </div>
    <StatusText status={tile.status} label={tile.status_label} />
    <p class="text-xs text-base-content/60">{tile.baseline_label}</p>
    <Sparkline
      values={tile.spark.map((point) => point.value)}
      bandLow={tile.band_low}
      bandHigh={tile.band_high}
      label="{tile.label} nos últimos 14 dias"
    />
  </div>
</article>
