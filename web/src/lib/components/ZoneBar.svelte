<script lang="ts">
  import type { ZoneTime } from "$lib/data/types";
  import { duration } from "$lib/format";

  const { zones }: { zones: ZoneTime[] } = $props();

  const total = $derived(zones.reduce((sum, zone) => sum + zone.seconds, 0) || 1);
  const shade = (zone: number): string =>
    `color-mix(in oklab, var(--ramp-hr-high) ${(zone - 1) * 25}%, var(--ramp-hr-low))`;
  const NAMES = ["muito leve", "leve", "moderado", "limiar", "máximo"];
</script>

<div class="flex flex-col gap-3">
  <div
    class="flex h-4 w-full overflow-hidden rounded-field"
    role="img"
    aria-label="Tempo em cada zona de FC"
  >
    {#each zones as zone (zone.zone)}
      {#if zone.seconds > 0}
        <span
          class="h-full border-r-2 border-[var(--color-base-100)] last:border-r-0"
          style:width="{(zone.seconds / total) * 100}%"
          style:background={shade(zone.zone)}
        ></span>
      {/if}
    {/each}
  </div>
  <ul class="flex flex-col gap-1.5 text-xs">
    {#each zones as zone (zone.zone)}
      <li class="grid grid-cols-[1fr_auto_auto] items-center gap-3">
        <span class="inline-flex items-center gap-1.5 font-semibold"
          ><i class="size-2.5 rounded-full" style:background={shade(zone.zone)}></i>Z{zone.zone} · {NAMES[
            zone.zone - 1
          ]}</span
        >
        <span class="text-base-content/70 tabular-nums"
          >{duration(zone.seconds)} · {Math.round((zone.seconds / total) * 100)}%</span
        >
        <span class="text-base-content/50 tabular-nums"
          >{zone.floor_bpm ?? "—"}{zone.ceiling_bpm ? `–${zone.ceiling_bpm - 1}` : "+"} bpm</span
        >
      </li>
    {/each}
  </ul>
</div>
