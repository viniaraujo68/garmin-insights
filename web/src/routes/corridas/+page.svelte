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
      label: "Data",
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
      label: "Pace sem calor",
      numeric: true,
      value: (run) => pace(run.heat_adjusted_pace_s_km),
      sortBy: (run) => run.heat_adjusted_pace_s_km,
      defaultSortDirection: "asc",
    },
    {
      key: "avg_hr",
      label: "FC",
      numeric: true,
      value: (run) => number(run.avg_hr),
      sortBy: (run) => run.avg_hr,
    },
    {
      key: "meters_per_beat",
      label: "m/bat",
      numeric: true,
      value: (run) => number(run.meters_per_beat, 2),
      sortBy: (run) => run.meters_per_beat,
    },
    {
      key: "performance_condition",
      label: "Condição",
      numeric: true,
      value: (run) => delta(run.performance_condition, 1),
      sortBy: (run) => run.performance_condition,
    },
    {
      key: "feels_like_c",
      label: "Sensação °C",
      numeric: true,
      value: (run) => number(run.feels_like_c),
      sortBy: (run) => run.feels_like_c,
    },
    {
      key: "cadence",
      label: "Cadência",
      numeric: true,
      value: (run) => number(run.cadence),
      sortBy: (run) => run.cadence,
      hiddenByDefault: true,
    },
    {
      key: "training_load",
      label: "Carga",
      numeric: true,
      value: (run) => number(run.training_load),
      sortBy: (run) => run.training_load,
    },
    {
      key: "training_effect_label",
      label: "Tipo",
      value: (run) => labelOf(TRAINING_EFFECT, run.training_effect_label),
    },
    {
      key: "rpe",
      label: "Esforço",
      numeric: true,
      value: (run) => number(run.rpe),
      sortBy: (run) => run.rpe,
      hiddenByDefault: true,
    },
  ];
</script>

<PageFrame
  title="Corridas"
  description="Todas as suas corridas: compare qualquer métrica ao longo do tempo, veja o desenho de cada percurso e abra uma corrida para os detalhes."
>
  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="explorador">
    <div class="card-body gap-3 p-5">
      <h2 id="explorador" class="text-base font-semibold">Explorador</h2>
      <RunExplorer runs={data.runs} />
    </div>
  </section>

  <section class="flex flex-col gap-3" aria-labelledby="percursos">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div>
        <h2 id="percursos" class="text-base font-semibold">Percursos</h2>
        <p class="text-xs text-base-content/70">
          Colorido pelo ritmo de cada trecho: mais escuro é mais rápido.
        </p>
      </div>
    </div>
    <ul class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
      {#each runs as run (run.activity_id)}
        {@const route = routesById.get(run.activity_id)}
        <li>
          <a
            href={resolve("/corridas/[id]", { id: run.activity_id })}
            class="card block border border-base-content/10 bg-base-100 p-3 transition-colors hover:border-primary/50"
          >
            {#if route}
              <RouteThumb {route} />
            {:else}
              <div class="grid aspect-[4/3] place-items-center text-xs text-base-content/40">
                sem GPS
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

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="tabela">
    <div class="card-body gap-3 p-5">
      <h2 id="tabela" class="text-base font-semibold">Tabela</h2>
      <DataTable
        rows={runs}
        {columns}
        rowKey={(run) => run.activity_id}
        onRowClick={(run) => goto(resolve("/corridas/[id]", { id: run.activity_id }))}
        label="Corridas"
        storageKey="garmin-insights:runs-table"
        sortLabel={(column) => `Ordenar por ${column.label}`}
      />
    </div>
  </section>
</PageFrame>
