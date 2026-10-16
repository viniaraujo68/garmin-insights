<script lang="ts">
  import { resolve } from "$app/paths";
  import type { EfficiencyPoint } from "$lib/data/types";
  import { dayMonth, number, pace } from "$lib/format";

  const { runs }: { runs: EfficiencyPoint[] } = $props();

  const rows = $derived(
    runs.filter((run) => run.pace_s_km !== null && run.heat_adjusted_pace_s_km !== null),
  );
  const extent = $derived.by(() => {
    const values = rows.flatMap((run) => [run.pace_s_km ?? 0, run.heat_adjusted_pace_s_km ?? 0]);
    const low = Math.min(...values) - 10;
    const high = Math.max(...values) + 10;
    return [low, high] as const;
  });
  const position = (value: number | null): number =>
    (((value ?? 0) - extent[0]) / (extent[1] - extent[0])) * 100;
</script>

<div class="flex flex-col gap-1.5">
  <div class="flex justify-between pl-24 text-xs text-base-content/60 tabular-nums">
    <span>{pace(extent[0])}/km · mais rápido</span>
    <span>mais lento · {pace(extent[1])}/km</span>
  </div>
  {#each [...rows].reverse() as run (run.activity_id)}
    <a
      href={resolve("/corridas/[id]", { id: run.activity_id })}
      class="grid grid-cols-[5.5rem_1fr] items-center gap-2 rounded-field px-1 py-0.5 text-xs hover:bg-base-200/60"
    >
      <span class="tabular-nums"
        >{dayMonth(run.date)}
        <span class="text-base-content/50">{number(run.feels_like_c)}°</span></span
      >
      <span class="relative h-5">
        <span
          class="absolute top-1/2 h-0.5 -translate-y-1/2 bg-base-content/20"
          style:left="{position(run.heat_adjusted_pace_s_km)}%"
          style:width="{Math.max(
            0.5,
            position(run.pace_s_km) - position(run.heat_adjusted_pace_s_km),
          )}%"
        ></span>
        <span
          class="absolute top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[var(--color-base-100)]"
          style:left="{position(run.heat_adjusted_pace_s_km)}%"
          style:background="var(--series-1)"
          title="sem calor {pace(run.heat_adjusted_pace_s_km)}"
        ></span>
        <span
          class="absolute top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[var(--color-base-100)]"
          style:left="{position(run.pace_s_km)}%"
          style:background="var(--series-2)"
          title="real {pace(run.pace_s_km)}"
        ></span>
      </span>
    </a>
  {/each}
  <div class="mt-1 flex gap-4 pl-24 text-xs text-base-content/70">
    <span class="inline-flex items-center gap-1.5"
      ><i class="size-2.5 rounded-full" style:background="var(--series-2)"></i>pace real</span
    >
    <span class="inline-flex items-center gap-1.5"
      ><i class="size-2.5 rounded-full" style:background="var(--series-1)"></i>num dia fresco</span
    >
  </div>
</div>
