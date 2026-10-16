<script lang="ts" module>
  export interface ScatterPoint {
    x: number;
    y: number;
    tone: "accent" | "muted" | number;
    tooltip: string[];
    activityId?: string;
  }
</script>

<script lang="ts">
  import { Chart, type ChartConfiguration } from "chart.js";
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { registerCharts } from "$lib/charts/register";
  import { readChartColors } from "$lib/charts/theme";
  import { interpolate } from "$lib/color";

  const {
    points,
    fit,
    formatX,
    formatY,
    ariaLabel,
    xLabel,
    reverseY = false,
    height = "h-64",
    pointRadius = 5,
  }: {
    points: ScatterPoint[];
    fit?: { x1: number; y1: number; x2: number; y2: number; label: string } | null;
    formatX: (value: number) => string;
    formatY: (value: number) => string;
    ariaLabel: string;
    xLabel: string;
    reverseY?: boolean;
    height?: string;
    pointRadius?: number;
  } = $props();

  const theme = getThemeContext();
  let canvas = $state<HTMLCanvasElement>();
  let host = $state<HTMLDivElement>();

  $effect(() => {
    const element = canvas;
    const container = host;
    const items = points;
    const line = fit;
    void theme.dark;
    if (!element || !container) return;
    registerCharts();
    const colors = readChartColors(container);
    const warm = interpolate(colors.hrLow, colors.hrHigh);
    const resolved = items.map((item) => {
      if (item.tone === "accent") return colors.series[0] ?? colors.ink;
      if (item.tone === "muted") return colors.neutral;
      return warm(item.tone);
    });

    const config: ChartConfiguration<"scatter"> = {
      type: "scatter",
      data: {
        datasets: [
          ...(line
            ? [
                {
                  showLine: true,
                  label: line.label,
                  data: [
                    { x: line.x1, y: line.y1 },
                    { x: line.x2, y: line.y2 },
                  ],
                  borderColor: colors.muted,
                  borderDash: [6, 5],
                  borderWidth: 1.5,
                  pointRadius: 0,
                  pointHoverRadius: 0,
                },
              ]
            : []),
          {
            label: "pontos",
            data: items.map((item) => ({ x: item.x, y: item.y })),
            backgroundColor: resolved,
            borderColor: colors.surface,
            borderWidth: 1.5,
            pointRadius,
            pointHoverRadius: pointRadius + 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        onClick: (_event, elements, chart) => {
          const hit = elements.find(
            (element) => chart.data.datasets[element.datasetIndex]?.label === "pontos",
          );
          const activityId = hit ? items[hit.index]?.activityId : undefined;
          if (activityId) void goto(resolve("/corridas/[id]", { id: activityId }));
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
            filter: (item) => item.dataset.label === "pontos",
            callbacks: {
              title: () => "",
              label: (item) => items[item.dataIndex]?.tooltip ?? [],
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            grace: "2%",
            grid: { display: false },
            border: { color: colors.grid },
            title: { display: true, text: xLabel, color: colors.muted },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 6,
              callback: (value) => formatX(Number(value)),
            },
          },
          y: {
            reverse: reverseY,
            grace: "8%",
            grid: { color: colors.grid },
            border: { display: false },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 6,
              callback: (value) => formatY(Number(value)),
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
