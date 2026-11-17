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
    if (value === null) return "no reading";
    if (value >= 5) return "very good day";
    if (value >= 1) return "good day";
    if (value > -2) return "normal";
    if (value > -5) return "below normal";
    return "bad day";
  };

  const stats = $derived([
    { label: "Distance", value: km(run.distance_km, 2) },
    { label: "Time", value: clock((run.duration_min ?? 0) * 60) },
    { label: "Pace", value: `${pace(run.pace_s_km)}/km` },
    { label: "Avg HR", value: `${number(run.avg_hr)} bpm`, hint: `max ${number(run.max_hr)}` },
    {
      label: "Load",
      value: number(run.training_load),
      hint: labelOf(TRAINING_EFFECT, run.training_effect_label),
    },
    {
      label: "Aerobic Training Effect",
      value: number(run.aerobic_te, 1),
      hint: `anaerobic ${number(run.anaerobic_te, 1)}`,
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
    <nav class="mt-2 flex gap-2" aria-label="Other runs">
      {#if data.previousId}<a
          class="btn btn-ghost btn-sm"
          href={resolve("/runs/[id]", { id: data.previousId })}>← previous</a
        >{/if}
      {#if data.nextId}<a
          class="btn btn-ghost btn-sm"
          href={resolve("/runs/[id]", { id: data.nextId })}>next →</a
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
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="map">
      <div class="card-body gap-3 p-4 sm:p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 id="map" class="text-base font-semibold">Route</h2>
          <SegmentedControl
            options={COLOR_BY_OPTIONS}
            bind:value={colorBy}
            label="Colour the route by"
            caption="Colour by"
            size="sm"
          />
        </div>
        {#if run.has_gps}
          <RouteMap streams={data.detail.streams} zones={data.detail.zones} {colorBy} bind:hover />
        {:else}
          <p class="text-sm text-base-content/70">Run without GPS.</p>
        {/if}
      </div>
    </section>

    <div class="flex flex-col gap-4">
      <section class="card border border-base-content/10 bg-base-100" aria-labelledby="conditions">
        <div class="card-body gap-4 p-5">
          <h2 id="conditions" class="text-base font-semibold">Conditions</h2>
          <dl class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt class="text-xs text-base-content/70">Temperature</dt>
              <dd class="font-semibold tabular-nums">{number(weather.temperature_c)} °C</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Feels like</dt>
              <dd class="font-semibold tabular-nums">{number(weather.feels_like_c)} °C</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Humidity</dt>
              <dd class="font-semibold tabular-nums">{number(weather.humidity_pct)}%</dd>
            </div>
            <div>
              <dt class="text-xs text-base-content/70">Dew point</dt>
              <dd class="font-semibold tabular-nums">{number(weather.dew_point_c)} °C</dd>
            </div>
          </dl>
          <div class="flex flex-col gap-1 rounded-box bg-base-200/60 p-3">
            <p class="text-xs text-base-content/70">Equivalent pace on a cool day</p>
            <p class="text-2xl font-semibold tabular-nums">
              {pace(run.heat_adjusted_pace_s_km)}/km
            </p>
            <p class="text-xs text-base-content/70">
              Heat and humidity cost about {number(run.heat_slowdown_pct, 1)}% of pace (Hadley rule:
              temperature + dew point).
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-xs text-base-content/70">Average Performance Condition</p>
            <p class="text-2xl font-semibold tabular-nums">
              {delta(run.performance_condition, 1)}
              <span class="text-sm font-normal text-base-content/70"
                >{conditionText(run.performance_condition)}</span
              >
            </p>
            <p class="text-xs text-base-content/60">
              Comparison, during the run, between your pace and HR and your fitness level.
            </p>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs text-base-content/70">
            <span
              >Perceived effort <b class="text-base-content tabular-nums">{number(run.rpe)}/10</b
              ></span
            >
            <span
              >Body Battery <b class="text-base-content tabular-nums"
                >{number(run.body_battery_impact)}</b
              ></span
            >
            <span
              >Recovery HR <b class="text-base-content tabular-nums"
                >{run.recovery_hr === null ? "—" : `−${number(run.recovery_hr)} bpm`}</b
              ></span
            >
            <span
              >Elevation gain <b class="text-base-content tabular-nums"
                >{number(run.elevation_gain_m)} m</b
              ></span
            >
          </div>
        </div>
      </section>
      <section class="card border border-base-content/10 bg-base-100" aria-labelledby="zones">
        <div class="card-body gap-3 p-5">
          <h2 id="zones" class="text-base font-semibold">Time in HR zone</h2>
          <ZoneBar zones={data.detail.zones} />
        </div>
      </section>
    </div>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="curves">
    <div class="card-body gap-3 p-5">
      <div>
        <h2 id="curves" class="text-base font-semibold">The run, metre by metre</h2>
        <p class="text-xs text-base-content/70">
          Hover over any lane or the map: they all show the same point.
        </p>
      </div>
      <MetricLanes streams={data.detail.streams} zones={data.detail.zones} bind:hover />
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="splits">
    <div class="card-body gap-3 p-5">
      <h2 id="splits" class="text-base font-semibold">Splits per km</h2>
      <SplitsTable laps={data.detail.laps} />
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="technique">
    <div class="card-body gap-3 p-5">
      <div>
        <h2 id="technique" class="text-base font-semibold">Technique</h2>
        <p class="text-xs text-base-content/70">
          Run averages compared with Garmin's colour ranges (approximate). Running faster improves
          almost all of them.
        </p>
      </div>
      <TechniqueGrid {run} />
    </div>
  </section>
</PageFrame>
