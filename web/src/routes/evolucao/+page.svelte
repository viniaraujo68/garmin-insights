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
            `${number(value, 2)} m/bat`,
            `pace ${pace(point.pace_s_km)}/km · FC ${number(point.avg_hr)}`,
            `sensação ${number(point.feels_like_c)} °C`,
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
          label: "tendência",
        }
      : null,
  );
  const lastVo2 = $derived(performance.vo2max.at(-1)?.value ?? null);
  const tenK = $derived(performance.races.find((race) => race.distance === "10K"));

  const recordColumns: Column<RecordRow>[] = [
    { key: "label", label: "Recorde", hideable: false },
    { key: "value_display", label: "Marca", numeric: true, sortBy: (row) => row.value },
    { key: "date", label: "Data", value: (row) => date(row.date), sortBy: (row) => row.date },
  ];
</script>

<PageFrame
  title="Evolução"
  description="Se você está ficando mais rápido, mais eficiente e com melhor técnica, sem deixar o calor do Rio enganar a leitura."
>
  <div class="stats stats-vertical border border-base-content/10 bg-base-100 sm:stats-horizontal">
    <div class="stat">
      <div class="stat-title">Eficiência</div>
      <div class="stat-value text-2xl tabular-nums">
        {trend ? `${delta(trend.per_30_days, 2)}` : "—"}
      </div>
      <div class="stat-desc">m/bat por mês, já sem o efeito do calor</div>
    </div>
    <div class="stat">
      <div class="stat-title">VO2max</div>
      <div class="stat-value text-2xl tabular-nums">{number(lastVo2, 1)}</div>
      <div class="stat-desc">
        {performance.vo2max_per_30_days === null
          ? "sem tendência"
          : `${delta(performance.vo2max_per_30_days, 1)} por mês`}
      </div>
    </div>
    {#if tenK}
      <div class="stat">
        <div class="stat-title">Previsão 10K</div>
        <div class="stat-value text-2xl tabular-nums">{pace(tenK.current_seconds)}</div>
        <div class="stat-desc">{pace(tenK.current_seconds / tenK.km)}/km</div>
      </div>
    {/if}
    {#if performance.fitness_age}
      <div class="stat">
        <div class="stat-title">Idade fitness</div>
        <div class="stat-value text-2xl tabular-nums">
          {number(performance.fitness_age.fitness_age)}
        </div>
        <div class="stat-desc">idade real {number(performance.fitness_age.chronological_age)}</div>
      </div>
    {/if}
  </div>

  <div class="grid items-start gap-4 xl:grid-cols-[3fr_2fr]">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="eficiencia">
      <div class="card-body gap-3 p-5">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <h2 id="eficiencia" class="text-base font-semibold">Metros por batimento</h2>
          <SegmentedControl
            options={[
              { id: "heat", label: "Sem o calor" },
              { id: "raw", label: "Como medido" },
            ]}
            bind:value={view}
            label="Versão da eficiência"
            size="sm"
          />
        </div>
        <p class="text-xs text-base-content/70">
          Cada ponto é uma corrida, colorido pela sensação térmica (mais escuro = mais quente). "Sem
          o calor" corrige a velocidade pela regra de Hadley antes de dividir pela FC, para um dia
          quente não parecer perda de forma.
        </p>
        <ScatterFit
          points={efficiencyPoints}
          fit={trendLine}
          formatX={(value) => dayMonth(new Date(value).toISOString())}
          formatY={(value) => number(value, 2)}
          xLabel="data"
          ariaLabel="Eficiência por corrida"
          height="h-80"
          pointRadius={6}
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="calor">
      <div class="card-body gap-3 p-5">
        <h2 id="calor" class="text-base font-semibold">Quanto o calor te custou</h2>
        <p class="text-xs text-base-content/70">
          Para cada corrida, o pace real e o pace equivalente num dia fresco. Quanto maior o traço,
          mais o calor pesou.
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
                    label: "Projeção",
                    points: performance.vo2max_projection,
                    slot: 0,
                    dashed: true,
                  },
                ]
              : []),
          ]}
          format={(value) => number(value, 1)}
          ariaLabel="VO2max ao longo do tempo"
          legend={false}
          height="h-56"
        />
      </div>
    </section>
    {#if performance.fitness_age}
      <FitnessAgeCard age={performance.fitness_age} />
    {/if}
  </div>

  <section class="flex flex-col gap-3" aria-labelledby="provas">
    <div>
      <h2 id="provas" class="text-base font-semibold">Previsões de prova</h2>
      <p class="text-xs text-base-content/70">
        Do relógio, a partir do VO2max e do histórico. Tracejado: projeção. "Equivalente ao recorde"
        estima cada distância a partir do seu recorde mais longo (fórmula de Riegel); a diferença
        para a previsão mostra quanto você ainda não testou em prova.
      </p>
    </div>
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {#each performance.races as race (race.distance)}
        <RaceCard {race} />
      {/each}
    </div>
  </section>

  <section class="flex flex-col gap-3" aria-labelledby="forma">
    <div>
      <h2 id="forma" class="text-base font-semibold">Técnica</h2>
      <p class="text-xs text-base-content/70">
        Cada ponto é uma corrida. Como correr mais rápido muda todas essas medidas, o valor de cada
        corrida é ajustado para o mesmo ritmo, e assim treinos rápidos e lentos ficam comparáveis. A
        faixa verde é a média dos corredores, segundo a Garmin. A comparação é entre as últimas {performance.form_window_days /
          7} semanas e as anteriores.
      </p>
    </div>
    <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {#each performance.form as metric (metric.key)}
        <FormPanel {metric} />
      {/each}
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="recordes">
    <div class="card-body gap-3 p-5">
      <h2 id="recordes" class="text-base font-semibold">Recordes pessoais</h2>
      <p class="text-xs text-base-content/70">
        Os melhores trechos que o relógio registrou, inclusive dentro de treinos.
      </p>
      <DataTable
        rows={performance.records}
        columns={recordColumns}
        rowKey={(row) => row.type_id}
        label="Recordes"
        sortLabel={(column) => `Ordenar por ${column.label}`}
      />
    </div>
  </section>
</PageFrame>
