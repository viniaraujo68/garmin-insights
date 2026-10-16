<script lang="ts">
  import type { BaselineTile } from "$lib/data/types";
  import StatusText from "./StatusText.svelte";
  import TileChart from "./TileChart.svelte";

  const { tile }: { tile: BaselineTile } = $props();

  const UNIT: Record<string, string> = {
    hrv: "ms",
    resting_hr: "bpm",
    sleep: "pontos",
    steps: "passos",
  };
  const FIXED: Record<string, [number, number]> = {
    sleep: [0, 100],
    body_battery: [0, 100],
    stress: [0, 100],
  };
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
    <TileChart
      points={tile.spark}
      bandLow={tile.band_low}
      bandHigh={tile.band_high}
      unit={UNIT[tile.key] ?? ""}
      yDomain={FIXED[tile.key] ?? null}
      label="{tile.label} nos últimos 14 dias"
    />
  </div>
</article>
