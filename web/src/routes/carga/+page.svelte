<script lang="ts">
  import BarChart from "$lib/components/BarChart.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import StatusText from "$lib/components/StatusText.svelte";
  import TimeChart from "$lib/components/TimeChart.svelte";
  import { dayMonth, number } from "$lib/format";

  const { data } = $props();
  const load = $derived(data.load);
  const summary = $derived(load.summary);

  const SUMMARY_LABEL: Record<string, string> = {
    good: "na faixa",
    attention: "abaixo da faixa",
    bad: "acima da faixa",
    unknown: "sem dado",
  };

  const firstTraining = $derived(load.weeks.findIndex((week) => week.load > 0));
  const weeks = $derived(firstTraining < 0 ? [] : load.weeks.slice(firstTraining));
  const weekLabels = $derived(
    weeks.map((week, index) =>
      index === weeks.length - 1 ? `${dayMonth(week.week)}*` : dayMonth(week.week),
    ),
  );
  const firstGarminDay = $derived(load.days.findIndex((day) => (day.acute ?? 0) > 0));
  const garminDays = $derived(firstGarminDay < 0 ? [] : load.days.slice(firstGarminDay));
  const runsLabel = (runs: number): string => `${runs} ${runs === 1 ? "corrida" : "corridas"}`;
</script>

<PageFrame
  title="Carga"
  description="Se você está treinando o suficiente, demais ou de menos, e se a mistura de leve e forte está boa."
>
  <section
    class="card border border-base-content/10 bg-base-100"
    aria-labelledby="veredito"
    data-testid="load-summary"
  >
    <div class="card-body gap-3 p-5">
      <StatusText status={summary.status} label={SUMMARY_LABEL[summary.status] ?? "sem dado"} />
      <h2 id="veredito" class="text-xl font-semibold tracking-tight">{summary.headline}</h2>
      <p class="max-w-3xl text-sm text-base-content/80">{summary.detail}</p>
      {#if summary.easy_line}
        <p class="max-w-3xl text-sm text-base-content/80">{summary.easy_line}</p>
      {/if}
    </div>
  </section>

  <div class="grid gap-4 xl:grid-cols-2">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="volume">
      <div class="card-body gap-3 p-5">
        <h2 id="volume" class="text-base font-semibold">Quilômetros por semana</h2>
        <p class="text-xs text-base-content/70">
          Quanto você correu em cada semana (de segunda a domingo). A semana com * ainda está em
          andamento.
        </p>
        <BarChart
          labels={weekLabels}
          series={[{ label: "Km", values: weeks.map((week) => week.km), slot: 0 }]}
          format={(value) => `${number(value, 1)} km`}
          extraTooltip={(index) => {
            const week = weeks[index];
            return week ? [`${runsLabel(week.runs)} · ${number(week.minutes_run)} min`] : [];
          }}
          height="h-56"
          ariaLabel="Quilômetros por semana"
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="leve">
      <div class="card-body gap-3 p-5">
        <h2 id="leve" class="text-base font-semibold">Quanto do tempo foi leve</h2>
        <p class="text-xs text-base-content/70">
          % do tempo correndo nas zonas de FC 1 e 2. A regra 80/20: uns 80% leve deixa você aguentar
          mais treino e evoluir mais. Bem abaixo da linha = forte demais.
        </p>
        <BarChart
          labels={weekLabels}
          series={[{ label: "Leve", values: weeks.map((week) => week.easy_pct), slot: 2 }]}
          format={(value) => `${number(value)}%`}
          reference={{ value: 80, label: "meta 80%" }}
          extraTooltip={(index) => {
            const week = weeks[index];
            return week
              ? [
                  `${number(week.easy_min)} de ${number(week.easy_min + week.moderate_min + week.hard_min)} min leves`,
                ]
              : [];
          }}
          height="h-56"
          ariaLabel="Porcentagem de tempo leve por semana"
        />
      </div>
    </section>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="faixa">
    <div class="card-body gap-3 p-5">
      <h2 id="faixa" class="text-base font-semibold">Carga dos últimos 7 dias</h2>
      <p class="text-xs text-base-content/70">
        Cada ponto soma o esforço (a carga que a Garmin dá a cada treino) dos 7 dias anteriores. A
        faixa verde é o quanto você aguenta, calculada pelas suas últimas 4 semanas: dentro dela
        você evolui; abaixo está destreinando; acima o risco de lesão sobe.
      </p>
      <TimeChart
        series={[
          {
            label: "Carga dos últimos 7 dias",
            points: garminDays.map((day) => ({ date: day.date, value: day.acute })),
            slot: 0,
            width: 2.5,
          },
        ]}
        band={{
          label: "Faixa recomendada",
          low: garminDays.map((day) => ({ date: day.date, value: day.chronic_min })),
          high: garminDays.map((day) => ({ date: day.date, value: day.chronic_max })),
          slot: 2,
        }}
        format={(value) => number(value)}
        ariaLabel="Carga dos últimos 7 dias e faixa recomendada"
        height="h-56"
      />
    </div>
  </section>
</PageFrame>
