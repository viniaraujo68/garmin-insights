<script lang="ts">
  import type { RaceDistance } from "$lib/data/types";
  import { clock, pace } from "$lib/format";
  import TimeChart from "./TimeChart.svelte";

  const { race }: { race: RaceDistance } = $props();

  const tone = $derived.by(() => {
    if (race.delta_8w_seconds === null) return "";
    return race.delta_8w_seconds < 0 ? "text-success" : "text-error";
  });
  const deltaText = $derived(
    race.delta_8w_seconds === null
      ? "sem histórico de 8 semanas"
      : `${race.delta_8w_seconds < 0 ? "−" : "+"}${clock(Math.abs(race.delta_8w_seconds))} em 8 semanas`,
  );
</script>

<article class="card border border-base-content/10 bg-base-100">
  <div class="card-body gap-2 p-4">
    <div class="flex items-baseline justify-between gap-2">
      <h3 class="font-semibold">{race.label}</h3>
      <span class="text-xs text-base-content/60 tabular-nums"
        >{pace(race.current_seconds / race.km)}/km</span
      >
    </div>
    <p class="text-3xl font-semibold tracking-tight tabular-nums">{clock(race.current_seconds)}</p>
    <p class={["text-xs tabular-nums", tone]}>{deltaText}</p>
    <TimeChart
      series={[
        { label: "Previsão", points: race.series, slot: 0 },
        ...(race.projection
          ? [{ label: "Projeção", points: race.projection, slot: 0, dashed: true }]
          : []),
      ]}
      format={(value) => clock(value)}
      reverse
      legend={false}
      height="h-32"
      ariaLabel="Previsão de {race.label} ao longo do tempo"
    />
    <dl class="grid grid-cols-2 gap-1 text-xs text-base-content/70">
      <div>
        <dt>Seu recorde</dt>
        <dd class="font-semibold text-base-content tabular-nums">
          {race.record_seconds ? clock(race.record_seconds) : "—"}
        </dd>
      </div>
      <div>
        <dt>Equivalente ao recorde (Riegel)</dt>
        <dd class="font-semibold text-base-content tabular-nums">
          {race.riegel_seconds ? clock(race.riegel_seconds) : "—"}
        </dd>
      </div>
    </dl>
  </div>
</article>
