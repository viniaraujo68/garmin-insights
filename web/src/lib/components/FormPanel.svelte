<script lang="ts">
  import type { FormMetric } from "$lib/data/types";
  import { number, pace } from "$lib/format";
  import { TECHNIQUE, techniqueRank } from "$lib/technique";
  import StatusText from "./StatusText.svelte";
  import TimeChart from "./TimeChart.svelte";

  const { metric }: { metric: FormMetric } = $props();

  const HELP: Record<string, string> = {
    cadence: "Passos por minuto. Passos mais curtos e rápidos costumam reduzir o impacto.",
    stride_m: "Distância de cada passo. Depende da altura e da velocidade.",
    ground_contact_ms:
      "Quanto tempo o pé fica no chão a cada passo. Menos = passada mais elástica.",
    vertical_oscillation_cm:
      "Quanto o corpo sobe e desce a cada passo. Menos = menos energia gasta subindo.",
    vertical_ratio_pct: "A oscilação vertical dividida pela passada. Menos = mais eficiente.",
    power_w: "A força para manter o ritmo. Menos watts no mesmo ritmo = mais econômico.",
  };

  const digits = $derived(Math.min(2, Math.max(0, metric.digits)) as 0 | 1 | 2);
  const band = $derived(TECHNIQUE.find((item) => item.key === metric.key) ?? null);
  const rank = $derived(band && band.limits ? techniqueRank(band, metric.current) : null);
  const direction = $derived.by(() => {
    if (metric.lower_is_better === null) return "sem melhor ou pior";
    return metric.lower_is_better ? "↓ menor é melhor" : "↑ maior é melhor";
  });
  const tone = $derived.by(() => {
    if (
      metric.recent_delta === null ||
      metric.lower_is_better === null ||
      Math.abs(metric.recent_delta) < 10 ** -digits / 2
    )
      return "text-base-content/70";
    return metric.recent_delta < 0 === metric.lower_is_better ? "text-success" : "text-warning";
  });
  const referencePace = $derived(
    metric.reference_speed_kmh ? pace(3600 / metric.reference_speed_kmh) : null,
  );
  const points = $derived(
    metric.points.map((point) => ({ date: point.date, value: point.adjusted })),
  );
  const averageRange = $derived(
    band?.limits
      ? {
          label: "Média dos corredores",
          low: points.map((point) => ({ date: point.date, value: band.limits?.[1] ?? null })),
          high: points.map((point) => ({ date: point.date, value: band.limits?.[2] ?? null })),
          slot: 2,
        }
      : undefined,
  );
</script>

<article class="card border border-base-content/10 bg-base-100">
  <div class="card-body gap-2 p-4">
    <div class="flex items-baseline justify-between gap-2">
      <h3 class="font-semibold">{metric.label}</h3>
      <span class="badge badge-ghost badge-sm whitespace-nowrap">{direction}</span>
    </div>
    <p class="text-xs text-base-content/70">{HELP[metric.key] ?? ""}</p>
    <div class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
      <span class="text-2xl font-semibold tracking-tight tabular-nums"
        >{number(metric.current, digits)}
        <span class="text-sm font-normal text-base-content/60">{metric.unit}</span></span
      >
      {#if rank}<StatusText status={rank.status} label={rank.label} />{/if}
    </div>
    <p class="text-xs text-base-content/60">
      média das últimas 3 corridas{referencePace ? `, no ritmo de ${referencePace}/km` : ""}
    </p>
    <p class={["text-sm", tone]}>{metric.verdict}</p>
    <TimeChart
      series={[{ label: metric.label, points, slot: 0, dots: true, width: 1.5 }]}
      band={averageRange}
      format={(value) => `${number(value, digits)} ${metric.unit}`}
      ariaLabel="{metric.label} por corrida"
      legend={false}
      zero={false}
      height="h-40"
    />
  </div>
</article>
