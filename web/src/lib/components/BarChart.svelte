<script lang="ts" module>
  export interface BarSeries {
    label: string;
    values: (number | null)[];
    slot?: number;
    colors?: string[];
  }
</script>

<script lang="ts">
  import { Chart, type ChartConfiguration } from "chart.js";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { registerCharts } from "$lib/charts/register";
  import { readChartColors, seriesColor } from "$lib/charts/theme";

  const {
    labels,
    series,
    format,
    ariaLabel,
    stacked = false,
    height = "h-64",
    reference,
    extraTooltip,
    signedColors = false,
  }: {
    labels: string[];
    series: BarSeries[];
    format: (value: number) => string;
    ariaLabel: string;
    stacked?: boolean;
    height?: string;
    reference?: { value: number; label: string };
    extraTooltip?: (index: number) => string[];
    signedColors?: boolean;
  } = $props();

  const theme = getThemeContext();
  let canvas = $state<HTMLCanvasElement>();
  let host = $state<HTMLDivElement>();

  $effect(() => {
    const element = canvas;
    const container = host;
    const rows = labels;
    const bars = series;
    const line = reference;
    void theme.dark;
    if (!element || !container) return;
    registerCharts();
    const colors = readChartColors(container);

    const config: ChartConfiguration<"bar"> = {
      type: "bar",
      data: {
        labels: rows,
        datasets: bars.map((bar) => {
          const base = seriesColor(colors, bar.slot ?? 0);
          return {
            label: bar.label,
            data: bar.values,
            backgroundColor: signedColors
              ? bar.values.map((value) => ((value ?? 0) < 0 ? colors.critical : base))
              : (bar.colors ?? base),
            borderRadius: 4,
            borderSkipped: stacked ? false : "start",
            borderColor: colors.surface,
            borderWidth: stacked ? { top: 2 } : 0,
            maxBarThickness: 32,
          };
        }),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            display: bars.length > 1,
            position: "bottom",
            labels: {
              color: colors.ink,
              usePointStyle: true,
              boxWidth: 8,
              boxHeight: 8,
              padding: 14,
            },
          },
          tooltip: {
            backgroundColor: colors.surface,
            titleColor: colors.ink,
            bodyColor: colors.ink,
            borderColor: colors.grid,
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (item) => ` ${item.dataset.label ?? ""}: ${format(item.parsed.y ?? 0)}`,
              afterBody: (items) =>
                extraTooltip && items[0] ? extraTooltip(items[0].dataIndex) : [],
            },
          },
        },
        scales: {
          x: {
            stacked,
            grid: { display: false },
            border: { color: colors.grid },
            ticks: { color: colors.muted, maxRotation: 0, autoSkipPadding: 12 },
          },
          y: {
            stacked,
            beginAtZero: true,
            grid: { color: colors.grid },
            border: { display: false },
            ticks: {
              color: colors.muted,
              maxTicksLimit: 6,
              callback: (value) => format(Number(value)),
            },
          },
        },
      },
      plugins: line
        ? [
            {
              id: "reference",
              afterDatasetsDraw: (chart) => {
                const y = chart.scales["y"]?.getPixelForValue(line.value);
                if (y === undefined) return;
                const { ctx, chartArea } = chart;
                ctx.save();
                ctx.strokeStyle = colors.muted;
                ctx.setLineDash([5, 4]);
                ctx.beginPath();
                ctx.moveTo(chartArea.left, y);
                ctx.lineTo(chartArea.right, y);
                ctx.stroke();
                ctx.setLineDash([]);
                ctx.fillStyle = colors.muted;
                ctx.font = "11px sans-serif";
                ctx.fillText(line.label, chartArea.left + 4, y - 4);
                ctx.restore();
              },
            },
          ]
        : [],
    };
    const chart = new Chart(element, config);
    return () => chart.destroy();
  });
</script>

<div bind:this={host} class={["relative w-full", height]} role="img" aria-label={ariaLabel}>
  <canvas bind:this={canvas}></canvas>
</div>
