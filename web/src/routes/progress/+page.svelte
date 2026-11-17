<script lang="ts">
  import { SegmentedControl } from "@viniaraujo68/plinth/components";
  import { DataTable, type Column } from "@viniaraujo68/plinth/table";
  import FitnessAgeCard from "$lib/components/FitnessAgeCard.svelte";
  import FormPanel from "$lib/components/FormPanel.svelte";
  import HeatDumbbell from "$lib/components/HeatDumbbell.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import RaceCard from "$lib/components/RaceCard.svelte";
  import ScatterFit from "$lib/components/ScatterFit.svelte";
  import TimeChart from "$lib/components/TimeChart.svelte";
  import type { RecordRow } from "$lib/data/types";
  import { date, dayMonth, delta, number, pace } from "$lib/format";

  const { data } = $props();
  const performance = $derived(data.performance);

  type EfficiencyView = "raw" | "heat";
  let view = $state<EfficiencyView>("heat");

  const time = (day: string): number => Date.parse(`${day}T12:00:00Z`);
  const heatTone = (celsius: number | null): number =>
    celsius === null ? 0.5 : Math.min(1, Math.max(0, (celsius - 15) / 20));

  const efficiencyPoints = $derived(
    performance.efficiency.flatMap((point) => {
      const value = view === "raw" ? point.meters_per_beat : point.heat_adjusted_meters_per_beat;
      if (value === null) return [];
      return [
        {
          x: time(point.date),
          y: value,
          tone: heatTone(point.feels_like_c),
          tooltip: [
            `${dayMonth(point.date)} · ${number(point.distance_km, 1)} km`,
            `${number(value, 2)} m/beat`,
            `pace ${pace(point.pace_s_km)}/km · HR ${number(point.avg_hr)}`,
            `feels like ${number(point.feels_like_c)} °C`,
          ],
          activityId: point.activity_id,
        },
      ];
    }),
  );
  const trend = $derived(
    view === "raw" ? performance.efficiency_trend : performance.heat_adjusted_trend,
  );
  const trendLine = $derived(
    trend
      ? {
          x1: time(trend.start_date),
          y1: trend.start_value,
          x2: time(trend.end_date),
          y2: trend.end_value,
          label: "trend",
        }
      : null,
  );
  const lastVo2 = $derived(performance.vo2max.at(-1)?.value ?? null);
  const tenK = $derived(performance.races.find((race) => race.distance === "10K"));

  const recordColumns: Column<RecordRow>[] = [
    { key: "label", label: "Record", hideable: false },
    { key: "value_display", label: "Mark", numeric: true, sortBy: (row) => row.value },
    { key: "date", label: "Date", value: (row) => date(row.date), sortBy: (row) => row.date },
  ];
</script>

<PageFrame
  title="Progress"
  description="Whether you are getting faster, more efficient and better in form, without Rio heat distorting the reading."
>
  <div class="stats stats-vertical border border-base-content/10 bg-base-100 sm:stats-horizontal">
    <div class="stat">
      <div class="stat-title">Efficiency</div>
      <div class="stat-value text-2xl tabular-nums">
        {trend ? `${delta(trend.per_30_days, 2)}` : "—"}
      </div>
      <div class="stat-desc">m/beat per month, with the heat effect removed</div>
    </div>
    <div class="stat">
      <div class="stat-title">VO2max</div>
      <div class="stat-value text-2xl tabular-nums">{number(lastVo2, 1)}</div>
      <div class="stat-desc">
        {performance.vo2max_per_30_days === null
          ? "no trend"
          : `${delta(performance.vo2max_per_30_days, 1)} per month`}
      </div>
    </div>
    {#if tenK}
      <div class="stat">
        <div class="stat-title">10K prediction</div>
        <div class="stat-value text-2xl tabular-nums">{pace(tenK.current_seconds)}</div>
        <div class="stat-desc">{pace(tenK.current_seconds / tenK.km)}/km</div>
      </div>
    {/if}
    {#if performance.fitness_age}
      <div class="stat">
        <div class="stat-title">Fitness Age</div>
        <div class="stat-value text-2xl tabular-nums">
          {number(performance.fitness_age.fitness_age)}
        </div>
        <div class="stat-desc">actual age {number(performance.fitness_age.chronological_age)}</div>
      </div>
    {/if}
  </div>

  <div class="grid items-start gap-4 xl:grid-cols-[3fr_2fr]">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="efficiency">
      <div class="card-body gap-3 p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 id="efficiency" class="text-base font-semibold">Metres per beat</h2>
          <SegmentedControl
            options={[
              { id: "heat", label: "Heat-adjusted" },
              { id: "raw", label: "As measured" },
            ]}
            bind:value={view}
            label="Efficiency version"
            size="sm"
          />
        </div>
        <p class="text-xs text-base-content/70">
          Each point is a run, coloured by feels-like temperature (darker = hotter). "Heat-adjusted"
          corrects speed with the Hadley rule before dividing by HR, so a hot day does not look like
          lost fitness.
        </p>
        <ScatterFit
          points={efficiencyPoints}
          fit={trendLine}
          formatX={(value) => dayMonth(new Date(value).toISOString())}
          formatY={(value) => number(value, 2)}
          xLabel="date"
          ariaLabel="Efficiency per run"
          height="h-80"
          pointRadius={6}
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="heat">
      <div class="card-body gap-3 p-5">
        <h2 id="heat" class="text-base font-semibold">What the heat cost you</h2>
        <p class="text-xs text-base-content/70">
          For each run, the actual pace and the equivalent pace on a cool day. The longer the bar,
          the more the heat weighed.
        </p>
        <HeatDumbbell runs={performance.efficiency} />
      </div>
    </section>
  </div>

  <div class="grid gap-4 xl:grid-cols-[2fr_1fr]">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="vo2">
      <div class="card-body gap-3 p-5">
        <h2 id="vo2" class="text-base font-semibold">VO2max</h2>
        <p class="text-xs text-base-content/70">{performance.projection_note}</p>
        <TimeChart
          series={[
            { label: "VO2max", points: performance.vo2max, slot: 0, dots: true },
            ...(performance.vo2max_projection
              ? [
                  {
                    label: "Projection",
                    points: performance.vo2max_projection,
                    slot: 0,
                    dashed: true,
                  },
                ]
              : []),
          ]}
          format={(value) => number(value, 1)}
          ariaLabel="VO2max over time"
          legend={false}
          height="h-56"
        />
      </div>
    </section>
    {#if performance.fitness_age}
      <FitnessAgeCard age={performance.fitness_age} />
    {/if}
  </div>

  <section class="flex flex-col gap-3" aria-labelledby="races">
    <div>
      <h2 id="races" class="text-base font-semibold">Race predictions</h2>
      <p class="text-xs text-base-content/70">
        From the watch, based on VO2max and history. Dashed: projection. "Record equivalent"
        estimates each distance from your longest record (Riegel formula); the difference from the
        prediction shows how much you have not yet tested in a race.
      </p>
    </div>
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {#each performance.races as race (race.distance)}
        <RaceCard {race} />
      {/each}
    </div>
  </section>

  <section class="flex flex-col gap-3" aria-labelledby="form">
    <div>
      <h2 id="form" class="text-base font-semibold">Technique</h2>
      <p class="text-xs text-base-content/70">
        Each point is a run. Because running faster changes all of these measures, each run's value
        is adjusted to the same pace, so fast and slow workouts are comparable. The green band is
        the average runner, according to Garmin. The comparison is between the last {performance.form_window_days /
          7} weeks and the ones before.
      </p>
    </div>
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {#each performance.form as metric (metric.key)}
        <FormPanel {metric} />
      {/each}
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="records">
    <div class="card-body gap-3 p-5">
      <h2 id="records" class="text-base font-semibold">Personal records</h2>
      <p class="text-xs text-base-content/70">
        The best stretches the watch recorded, including within workouts.
      </p>
      <DataTable
        rows={performance.records}
        columns={recordColumns}
        rowKey={(row) => row.type_id}
        label="Records"
        sortLabel={(column) => `Sort by ${column.label}`}
      />
    </div>
  </section>
</PageFrame>
