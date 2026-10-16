<script lang="ts">
  import { resolve } from "$app/paths";
  import { SegmentedControl } from "@viniaraujo68/plinth/components";
  import MetricLanes from "$lib/components/MetricLanes.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import RouteMap from "$lib/components/RouteMap.svelte";
  import SplitsTable from "$lib/components/SplitsTable.svelte";
  import TechniqueGrid from "$lib/components/TechniqueGrid.svelte";
  import ZoneBar from "$lib/components/ZoneBar.svelte";
  import { clock, dayTitle, delta, km, number, pace } from "$lib/format";
  import { labelOf, TRAINING_EFFECT } from "$lib/labels";
  import { COLOR_BY_OPTIONS, type ColorBy } from "$lib/streams";

  const { data } = $props();

  const run = $derived(data.detail.summary);
  const weather = $derived(data.detail.weather);
  let colorBy = $state<ColorBy>("pace");
  let hover = $state<number | null>(null);

  const conditionText = (value: number | null): string => {
    if (value === null) return "sem leitura";
    if (value >= 5) return "dia muito bom";
    if (value >= 1) return "dia bom";
    if (value > -2) return "normal";
    if (value > -5) return "abaixo do normal";
    return "dia ruim";
  };

  const stats = $derived([
    { label: "Distância", value: km(run.distance_km, 2) },
    { label: "Tempo", value: clock((run.duration_min ?? 0) * 60) },
    { label: "Pace", value: `${pace(run.pace_s_km)}/km` },
    { label: "FC média", value: `${number(run.avg_hr)} bpm`, hint: `máx ${number(run.max_hr)}` },
    {
      label: "Carga",
      value: number(run.training_load),
      hint: labelOf(TRAINING_EFFECT, run.training_effect_label),
    },
    {
      label: "Efeito aeróbico",
      value: number(run.aerobic_te, 1),
      hint: `anaeróbico ${number(run.anaerobic_te, 1)}`,
    },
  ]);
</script>

<PageFrame
  title={dayTitle(run.date)}
  description="{km(run.distance_km, 2)} · {pace(run.pace_s_km)}/km · {labelOf(
    TRAINING_EFFECT,
    run.training_effect_label,
  )}"
  breadcrumbs
>
  {#snippet header()}
    <nav class="mt-2 flex gap-2" aria-label="Outras corridas">
      {#if data.previousId}<a
          class="btn btn-ghost btn-sm"
          href={resolve("/corridas/[id]", { id: data.previousId })}>← anterior</a
        >{/if}
      {#if data.nextId}<a
          class="btn btn-ghost btn-sm"
          href={resolve("/corridas/[id]", { id: data.nextId })}>próxima →</a
        >{/if}
    </nav>
  {/snippet}

  <div class="stats stats-vertical border border-base-content/10 bg-base-100 sm:stats-horizontal">
    {#each stats as stat (stat.label)}
      <div class="stat">
        <div class="stat-title">{stat.label}</div>
        <div class="stat-value text-2xl tabular-nums">{stat.value}</div>
        {#if stat.hint}<div class="stat-desc">{stat.hint}</div>{/if}
      </div>
    {/each}
  </div>

  <div class="grid gap-4 xl:grid-cols-[2fr_1fr]">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="mapa">
      <div class="card-body gap-3 p-4 sm:p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 id="mapa" class="text-base font-semibold">Percurso</h2>
          <SegmentedControl
            options={COLOR_BY_OPTIONS}
            bind:value={colorBy}
            label="Colorir o percurso por"
            caption="Colorir por"
            size="sm"
          />
        </div>
        {#if run.has_gps}
          <RouteMap streams={data.detail.streams} zones={data.detail.zones} {colorBy} bind:hover />
        {:else}
          <p class="text-sm text-base-content/70">Corrida sem GPS.</p>
        {/if}
      </div>
    </section>

    <div class="flex flex-col gap-4">
      <section class="card border border-base-content/10 bg-base-100" aria-labelledby="condicoes">
        <div class="card-body gap-4 p-5">
          <h2 id="condicoes" class="text-base font-semibold">Condições do dia</h2>
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt class="text-xs text-base-content/70">Temperatura</dt>
              <dd class="font-semibold tabular-nums">{number(weather.temperature_c)} °C</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Sensação</dt>
              <dd class="font-semibold tabular-nums">{number(weather.feels_like_c)} °C</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Umidade</dt>
              <dd class="font-semibold tabular-nums">{number(weather.humidity_pct)}%</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Ponto de orvalho</dt>
              <dd class="font-semibold tabular-nums">{number(weather.dew_point_c)} °C</dd>
            </div>
          </dl>
          <div class="flex flex-col gap-1 rounded-box bg-base-200/60 p-3">
            <p class="text-xs text-base-content/70">Pace equivalente num dia fresco</p>
            <p class="text-2xl font-semibold tabular-nums">
              {pace(run.heat_adjusted_pace_s_km)}/km
            </p>
            <p class="text-xs text-base-content/70">
              O calor e a umidade custaram cerca de {number(run.heat_slowdown_pct, 1)}% de ritmo
              (regra de Hadley: temperatura + ponto de orvalho).
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-xs text-base-content/70">Condição de desempenho média</p>
            <p class="text-2xl font-semibold tabular-nums">
              {delta(run.performance_condition, 1)}
              <span class="text-sm font-normal text-base-content/70"
                >{conditionText(run.performance_condition)}</span
              >
            </p>
            <p class="text-xs text-base-content/60">
              Comparação, durante a corrida, entre o seu pace e FC e o seu nível de condicionamento.
            </p>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs text-base-content/70">
            <span
              >Esforço percebido <b class="text-base-content tabular-nums">{number(run.rpe)}/10</b
              ></span
            >
            <span
              >Body Battery <b class="text-base-content tabular-nums"
                >{number(run.body_battery_impact)}</b
              ></span
            >
            <span
              >FC de recuperação <b class="text-base-content tabular-nums"
                >{run.recovery_hr === null ? "—" : `−${number(run.recovery_hr)} bpm`}</b
              ></span
            >
            <span
              >Subida <b class="text-base-content tabular-nums">{number(run.elevation_gain_m)} m</b
              ></span
            >
          </div>
        </div>
      </section>
      <section class="card border border-base-content/10 bg-base-100" aria-labelledby="zonas">
        <div class="card-body gap-3 p-5">
          <h2 id="zonas" class="text-base font-semibold">Tempo por zona de FC</h2>
          <ZoneBar zones={data.detail.zones} />
        </div>
      </section>
    </div>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="curvas">
    <div class="card-body gap-3 p-5">
      <div>
        <h2 id="curvas" class="text-base font-semibold">A corrida metro a metro</h2>
        <p class="text-xs text-base-content/70">
          Passe o mouse em qualquer faixa ou no mapa: todas mostram o mesmo ponto.
        </p>
      </div>
      <MetricLanes streams={data.detail.streams} bind:hover />
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="splits">
    <div class="card-body gap-3 p-5">
      <h2 id="splits" class="text-base font-semibold">Splits por km</h2>
      <SplitsTable laps={data.detail.laps} />
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="tecnica">
    <div class="card-body gap-3 p-5">
      <div>
        <h2 id="tecnica" class="text-base font-semibold">Técnica</h2>
        <p class="text-xs text-base-content/70">
          Médias da corrida comparadas às faixas de cor da Garmin (aproximadas). Correr mais rápido
          melhora quase todas.
        </p>
      </div>
      <TechniqueGrid {run} />
    </div>
  </section>
</PageFrame>
