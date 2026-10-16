<script lang="ts">
  import type { FormMetric } from "$lib/data/types";
  import { number } from "$lib/format";
  import ScatterFit from "./ScatterFit.svelte";

  const { metric, windowDays }: { metric: FormMetric; windowDays: number } = $props();

  const digits = $derived(Math.min(2, Math.max(0, metric.digits)) as 0 | 1 | 2);
  const speeds = $derived(metric.points.map((point) => point.speed_kmh));
  const fit = $derived(
    metric.fit_slope === null || metric.fit_intercept === null || speeds.length < 2
      ? null
      : {
          x1: Math.min(...speeds),
          y1: metric.fit_slope * Math.min(...speeds) + metric.fit_intercept,
          x2: Math.max(...speeds),
          y2: metric.fit_slope * Math.max(...speeds) + metric.fit_intercept,
          label: "tendência pela velocidade",
        },
  );
  const tone = $derived.by(() => {
    if (
      metric.recent_delta === null ||
      metric.lower_is_better === null ||
      Math.abs(metric.recent_delta) < 10 ** -digits / 2
    )
      return "text-base-content/70";
    return metric.recent_delta < 0 === metric.lower_is_better ? "text-success" : "text-warning";
  });
</script>

<article class="card border border-base-content/10 bg-base-100">
  <div class="card-body gap-2 p-4">
    <h3 class="font-semibold">{metric.label}</h3>
    <p class={["text-sm", tone]}>{metric.verdict}</p>
    <ScatterFit
      points={metric.points.map((point) => ({
        x: point.speed_kmh,
        y: point.value,
        tone: point.recent ? "accent" : "muted",
        tooltip: [
          `${point.date.slice(8, 10)}/${point.date.slice(5, 7)}`,
          `${number(point.speed_kmh, 1)} km/h`,
          `${number(point.value, digits)} ${metric.unit}`,
        ],
      }))}
      {fit}
      formatX={(value) => number(value, 1)}
      formatY={(value) => number(value, digits)}
      xLabel="velocidade (km/h)"
      height="h-44"
      ariaLabel="{metric.label} pela velocidade"
    />
    <p class="text-xs text-base-content/60">
      Azul: últimas {windowDays / 7} semanas ({metric.recent_count}). Cinza: antes ({metric.earlier_count}).
    </p>
  </div>
</article>
