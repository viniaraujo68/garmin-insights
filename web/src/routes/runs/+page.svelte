<script lang="ts">
  import { resolve } from "$app/paths";
  import { goto } from "$app/navigation";
  import { DataTable, type Column } from "@viniaraujo68/plinth/table";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import RouteThumb from "$lib/components/RouteThumb.svelte";
  import RunExplorer from "$lib/components/RunExplorer.svelte";
  import type { ActivitySummary } from "$lib/data/types";
  import { date, delta, km, number, pace } from "$lib/format";
  import { labelOf, TRAINING_EFFECT } from "$lib/labels";

  const { data } = $props();

  const runs = $derived([...data.runs].reverse());
  const routesById = $derived(
    new Map(data.routes.routes.map((route) => [route.activity_id, route])),
  );

  const columns: Column<ActivitySummary>[] = [
    {
      key: "date",
      label: "Date",
      value: (run) => date(run.date),
      sortBy: (run) => run.date,
      hideable: false,
    },
    {
      key: "distance_km",
      label: "Km",
      numeric: true,
      value: (run) => number(run.distance_km, 2),
      sortBy: (run) => run.distance_km,
    },
    {
      key: "pace_s_km",
      label: "Pace",
      numeric: true,
      value: (run) => pace(run.pace_s_km),
      sortBy: (run) => run.pace_s_km,
      defaultSortDirection: "asc",
    },
    {
      key: "heat_adjusted_pace_s_km",
      label: "Heat-adjusted pace",
      numeric: true,
      value: (run) => pace(run.heat_adjusted_pace_s_km),
      sortBy: (run) => run.heat_adjusted_pace_s_km,
      defaultSortDirection: "asc",
    },
    {
      key: "avg_hr",
      label: "HR",
      numeric: true,
      value: (run) => number(run.avg_hr),
      sortBy: (run) => run.avg_hr,
    },
    {
      key: "meters_per_beat",
      label: "m/beat",
      numeric: true,
      value: (run) => number(run.meters_per_beat, 2),
      sortBy: (run) => run.meters_per_beat,
    },
    {
      key: "performance_condition",
      label: "Condition",
      numeric: true,
      value: (run) => delta(run.performance_condition, 1),
      sortBy: (run) => run.performance_condition,
    },
    {
      key: "feels_like_c",
      label: "Feels like °C",
      numeric: true,
      value: (run) => number(run.feels_like_c),
      sortBy: (run) => run.feels_like_c,
    },
    {
      key: "cadence",
      label: "Cadence",
      numeric: true,
      value: (run) => number(run.cadence),
      sortBy: (run) => run.cadence,
      hiddenByDefault: true,
    },
    {
      key: "training_load",
      label: "Load",
      numeric: true,
      value: (run) => number(run.training_load),
      sortBy: (run) => run.training_load,
    },
    {
      key: "training_effect_label",
      label: "Type",
      value: (run) => labelOf(TRAINING_EFFECT, run.training_effect_label),
    },
    {
      key: "rpe",
      label: "RPE",
      numeric: true,
      value: (run) => number(run.rpe),
      sortBy: (run) => run.rpe,
      hiddenByDefault: true,
    },
  ];
</script>

<PageFrame
  title="Runs"
  description="All your runs: compare any metric over time, see the shape of each route and open a run for the details."
>
  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="explorer">
    <div class="card-body gap-3 p-5">
      <h2 id="explorer" class="text-base font-semibold">Explorer</h2>
      <RunExplorer runs={data.runs} />
    </div>
  </section>

  <section class="flex flex-col gap-3" aria-labelledby="routes">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 id="routes" class="text-base font-semibold">Routes</h2>
        <p class="text-xs text-base-content/70">
          Coloured by the pace of each stretch: darker is faster.
        </p>
      </div>
    </div>
    <ul class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
      {#each runs as run (run.activity_id)}
        {@const route = routesById.get(run.activity_id)}
        <li>
          <a
            href={resolve("/runs/[id]", { id: run.activity_id })}
            class="card block border border-base-content/10 bg-base-100 p-3 transition-colors hover:border-primary/50"
          >
            {#if route}
              <RouteThumb {route} />
            {:else}
              <div class="grid aspect-[4/3] place-items-center text-xs text-base-content/40">
                no GPS
              </div>
            {/if}
            <p class="mt-1 text-sm font-semibold">{date(run.date)}</p>
            <p class="text-xs text-base-content/70 tabular-nums">
              {km(run.distance_km)} · {pace(run.pace_s_km)}/km
            </p>
          </a>
        </li>
      {/each}
    </ul>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="table">
    <div class="card-body gap-3 p-5">
      <h2 id="table" class="text-base font-semibold">Table</h2>
      <DataTable
        rows={runs}
        {columns}
        rowKey={(run) => run.activity_id}
        onRowClick={(run) => goto(resolve("/runs/[id]", { id: run.activity_id }))}
        label="Runs"
        storageKey="garmin-insights:runs-table"
        sortLabel={(column) => `Sort by ${column.label}`}
      />
    </div>
  </section>
</PageFrame>
