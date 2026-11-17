<script lang="ts">
  import { resolve } from "$app/paths";
  import { Chart, type ChartConfiguration, type ScatterDataPoint } from "chart.js";
  import { goto } from "$app/navigation";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { SegmentedControl } from "@viniaraujo68/plinth/components";
  import type { ActivitySummary } from "$lib/data/types";
  import { registerCharts } from "$lib/charts/register";
  import { readChartColors, seriesColor, seriesVar } from "$lib/charts/theme";
  import { dayMonth, km, number, pace } from "$lib/format";
  import { labelOf, TRAINING_EFFECT, TRAINING_EFFECT_ORDER } from "$lib/labels";

  type MetricId =
    "pace" | "heat" | "efficiency" | "hr" | "distance" | "cadence" | "condition" | "load";

  interface Metric {
    id: MetricId;
    label: string;
    value: (run: ActivitySummary) => number | null;
    format: (value: number) => string;
    reverse?: boolean;
    step?: number;
    hint: string;
  }

  const METRICS: Metric[] = [
    {
      id: "pace",
      label: "Pace",
      value: (run) => run.pace_s_km,
      format: (v) => `${pace(v)}/km`,
      reverse: true,
      step: 30,
      hint: "Higher on the chart = faster.",
    },
    {
      id: "heat",
      label: "Heat-adjusted pace",
      value: (run) => run.heat_adjusted_pace_s_km,
      format: (v) => `${pace(v)}/km`,
      reverse: true,
      step: 30,
      hint: "The pace you would have run on a cool day, correcting for temperature and humidity.",
    },
    {
      id: "efficiency",
      label: "Efficiency",
      value: (run) => run.meters_per_beat,
      format: (v) => `${number(v, 2)} m/beat`,
      hint: "Metres per beat: going up means improving.",
    },
    {
      id: "hr",
      label: "Avg HR",
      value: (run) => run.avg_hr,
      format: (v) => `${number(v)} bpm`,
      hint: "Average beats per minute during the run.",
    },
    {
      id: "distance",
      label: "Distance",
      value: (run) => run.distance_km,
      format: (v) => km(v),
      hint: "Kilometres per run.",
    },
    {
      id: "cadence",
      label: "Cadence",
      value: (run) => run.cadence,
      format: (v) => `${number(v)} spm`,
      hint: "Steps per minute.",
    },
    {
      id: "condition",
      label: "Condition",
      value: (run) => run.performance_condition,
      format: (v) => number(v, 1),
      hint: "Average Performance Condition: above 0 is a good day.",
    },
    {
      id: "load",
      label: "Load",
      value: (run) => run.training_load,
      format: (v) => number(v),
      hint: "Training load of the run (EPOC).",
    },
  ];

  const EFFECT_SLOT: Record<string, number> = {
    RECOVERY: 2,
    AEROBIC_BASE: 0,
    TEMPO: 3,
    LACTATE_THRESHOLD: 1,
    VO2MAX: 7,
    ANAEROBIC_CAPACITY: 6,
    SPRINT: 4,
  };

  const { runs }: { runs: ActivitySummary[] } = $props();

  const theme = getThemeContext();
  let metricId = $state<MetricId>("pace");
  let canvas = $state<HTMLCanvasElement>();
  let host = $state<HTMLDivElement>();

  const metric = $derived(METRICS.find((item) => item.id === metricId) ?? METRICS[0]!);
  const effects = $derived(
    TRAINING_EFFECT_ORDER.filter((effect) =>
      runs.some((run) => run.training_effect_label === effect),
    ),
  );
  const maxDistance = $derived(Math.max(1, ...runs.map((run) => run.distance_km ?? 0)));

  $effect(() => {
    const element = canvas;
    const container = host;
    const chosen = metric;
    const items = runs;
    const groups = effects;
    const largest = maxDistance;
    void theme.dark;
    if (!element || !container) return;

    registerCharts();
    const colors = readChartColors(container);
    type Point = ScatterDataPoint & { run: ActivitySummary };

    const config: ChartConfiguration<"scatter", Point[]> = {
      type: "scatter",
      data: {
        datasets: groups.map((effect) => ({
          label: labelOf(TRAINING_EFFECT, effect),
          data: items
            .filter((run) => run.training_effect_label === effect && chosen.value(run) !== null)
            .map((run) => ({
              x: Date.parse(`${run.date}T12:00:00Z`),
              y: chosen.value(run) ?? 0,
              run,
            })),
          backgroundColor: seriesColor(colors, EFFECT_SLOT[effect] ?? 0),
          borderColor: colors.surface,
          borderWidth: 2,
          pointRadius: (context) => {
            const raw = context.raw as Point | undefined;
            return 5 + ((raw?.run.distance_km ?? 0) / largest) * 9;
          },
          pointHoverRadius: (context) => {
            const raw = context.raw as Point | undefined;
            return 7 + ((raw?.run.distance_km ?? 0) / largest) * 9;
          },
        })),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        onClick: (_event, elements, chart) => {
          const element = elements[0];
          if (!element) return;
          const raw = chart.data.datasets[element.datasetIndex]?.data[element.index] as
            Point | undefined;
          if (raw) void goto(resolve("/runs/[id]", { id: raw.run.activity_id }));
        },
        onHover: (event, elements) => {
          const target = event.native?.target as HTMLElement | undefined;
          if (target) target.style.cursor = elements.length ? "pointer" : "default";
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: colors.surface,
            titleColor: colors.ink,
            bodyColor: colors.ink,
            borderColor: colors.grid,
            borderWidth: 1,
            padding: 10,
            callbacks: {
              title: (items) => {
                const raw = items[0]?.raw as Point | undefined;
                return raw ? `${dayMonth(raw.run.date)} · ${km(raw.run.distance_km)}` : "";
              },
              label: (item) => {
                const raw = item.raw as Point;
                return [
                  ` ${chosen.label}: ${chosen.format(raw.y ?? 0)}`,
                  ` Pace ${pace(raw.run.pace_s_km)}/km · HR ${number(raw.run.avg_hr)}`,
                  ` ${labelOf(TRAINING_EFFECT, raw.run.training_effect_label)}`,
                ];
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            grid: { display: false },
            border: { color: colors.grid },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 7,
              callback: (value) => dayMonth(new Date(Number(value)).toISOString()),
            },
          },
          y: {
            reverse: chosen.reverse ?? false,
            grace: "8%",
            grid: { color: colors.grid },
            border: { display: false },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 8,
              stepSize: chosen.step,
              callback: (value) => chosen.format(Number(value)),
            },
          },
        },
      },
    };
    const chart = new Chart(element, config);
    return () => chart.destroy();
  });
</script>

<div class="flex flex-col gap-3">
  <div class="flex flex-wrap items-center justify-between gap-3">
    <SegmentedControl
      options={METRICS.map((item) => ({ id: item.id, label: item.label }))}
      bind:value={metricId}
      label="Vertical axis metric"
      size="sm"
    />
    <ul class="flex flex-wrap gap-x-4 gap-y-1 text-xs" aria-label="Colours by workout type">
      {#each effects as effect (effect)}
        <li class="flex items-center gap-1.5">
          <span class="size-2.5 rounded-full" style:background={seriesVar(EFFECT_SLOT[effect] ?? 0)}
          ></span>
          {labelOf(TRAINING_EFFECT, effect)}
        </li>
      {/each}
      <li class="text-base-content/60">size = distance</li>
    </ul>
  </div>
  <p class="text-xs text-base-content/70">{metric.hint}</p>
  <div bind:this={host} class="relative h-80 w-full" role="img" aria-label="Runs by {metric.label}">
    <canvas bind:this={canvas}></canvas>
  </div>
</div>
