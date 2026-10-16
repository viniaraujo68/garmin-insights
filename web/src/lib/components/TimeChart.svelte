<script lang="ts" module>
  export interface TimePoint {
    date: string;
    value: number | null;
  }

  export interface TimeSeries {
    label: string;
    points: TimePoint[];
    slot: number;
    dashed?: boolean;
    dots?: boolean;
    width?: number;
    line?: boolean;
  }

  export interface TimeBand {
    label: string;
    low: TimePoint[];
    high: TimePoint[];
    slot: number;
  }
</script>

<script lang="ts">
  import { Chart, type ChartConfiguration, type ChartDataset } from "chart.js";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { registerCharts } from "$lib/charts/register";
  import { readChartColors, seriesColor } from "$lib/charts/theme";
  import { dayMonth } from "$lib/format";

  const {
    series,
    band,
    format,
    ariaLabel,
    reverse = false,
    step,
    min,
    max,
    height = "h-64",
    legend = true,
  }: {
    series: TimeSeries[];
    band?: TimeBand;
    format: (value: number) => string;
    ariaLabel: string;
    reverse?: boolean;
    step?: number;
    min?: number;
    max?: number;
    height?: string;
    legend?: boolean;
  } = $props();

  const theme = getThemeContext();
  let canvas = $state<HTMLCanvasElement>();
  let host = $state<HTMLDivElement>();

  const toXY = (points: TimePoint[]) =>
    points.map((point) => ({ x: Date.parse(`${point.date}T12:00:00Z`), y: point.value }));

  $effect(() => {
    const element = canvas;
    const container = host;
    const lines = series;
    const area = band;
    void theme.dark;
    if (!element || !container) return;
    registerCharts();
    const colors = readChartColors(container);

    const everything = [
      ...lines.flatMap((line) => line.points),
      ...(area ? [...area.low, ...area.high] : []),
    ];
    const allX = everything.map((point) => Date.parse(`${point.date}T12:00:00Z`));
    const allY = everything
      .map((point) => point.value)
      .filter((value): value is number => value !== null);
    const datasets: ChartDataset<"line", { x: number; y: number | null }[]>[] = [];
    if (area)
      datasets.push(
        {
          label: `${area.label} (mín)`,
          data: toXY(area.low),
          borderWidth: 0,
          pointRadius: 0,
          fill: false,
          borderColor: "transparent",
        },
        {
          label: area.label,
          data: toXY(area.high),
          borderWidth: 0,
          pointRadius: 0,
          fill: "-1",
          borderColor: "transparent",
          backgroundColor: colors.seriesSoft[area.slot] ?? colors.grid,
        },
      );

    for (const line of lines) {
      const color = seriesColor(colors, line.slot);
      datasets.push({
        label: line.label,
        data: toXY(line.points),
        borderColor: color,
        backgroundColor: color,
        borderWidth: line.line === false ? 0 : (line.width ?? 2),
        borderDash: line.dashed ? [6, 5] : [],
        showLine: line.line !== false,
        pointRadius: line.dots ? 3.5 : 0,
        pointHoverRadius: 5,
        pointBorderColor: colors.surface,
        pointBorderWidth: 1.5,
        tension: 0,
        spanGaps: true,
        fill: false,
      });
    }

    const config: ChartConfiguration<"line", { x: number; y: number | null }[]> = {
      type: "line",
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        parsing: false,
        interaction: { mode: "nearest", axis: "x", intersect: false },
        plugins: {
          legend: {
            display: legend,
            position: "bottom",
            labels: {
              color: colors.ink,
              usePointStyle: true,
              boxWidth: 8,
              boxHeight: 8,
              padding: 14,
              filter: (item) => !String(item.text).endsWith("(mín)"),
            },
          },
          tooltip: {
            backgroundColor: colors.surface,
            titleColor: colors.ink,
            bodyColor: colors.ink,
            borderColor: colors.grid,
            borderWidth: 1,
            padding: 10,
            filter: (item) =>
              !String(item.dataset.label).endsWith("(mín)") && item.parsed.y !== null,
            callbacks: {
              title: (items) =>
                items[0] ? dayMonth(new Date(items[0].parsed.x ?? 0).toISOString()) : "",
              label: (item) => {
                if (area && item.dataset.label === area.label) {
                  const low = area.low[item.dataIndex]?.value;
                  return ` ${area.label}: ${low === null || low === undefined ? "—" : format(low)}–${format(item.parsed.y ?? 0)}`;
                }
                return ` ${item.dataset.label ?? ""}: ${format(item.parsed.y ?? 0)}`;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            min: Math.min(...allX),
            max: Math.max(...allX),
            grid: { display: false },
            border: { color: colors.grid },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 7,
              callback: (value) => dayMonth(new Date(Number(value)).toISOString()),
            },
          },
          y: {
            reverse,
            min: min ?? (allY.length && Math.min(...allY) >= 0 && !reverse ? 0 : undefined),
            max,
            grace: "6%",
            grid: { color: colors.grid },
            border: { display: false },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 6,
              stepSize: step,
              callback: (value) => format(Number(value)),
            },
          },
        },
      },
    };
    const chart = new Chart(element, config);
    return () => chart.destroy();
  });
</script>

<div bind:this={host} class={["relative w-full", height]} role="img" aria-label={ariaLabel}>
  <canvas bind:this={canvas}></canvas>
</div>
