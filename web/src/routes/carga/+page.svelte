<script lang="ts">
  import BarChart from "$lib/components/BarChart.svelte";
  import FocusBars from "$lib/components/FocusBars.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import StatusText from "$lib/components/StatusText.svelte";
  import TimeChart from "$lib/components/TimeChart.svelte";
  import TrainingCalendar from "$lib/components/TrainingCalendar.svelte";
  import { dayMonth, delta, number } from "$lib/format";

  const { data } = $props();
  const load = $derived(data.load);

  const lastGarmin = $derived([...load.days].reverse().find((day) => day.acwr !== null) ?? null);
  const today = $derived(load.days.at(-1) ?? null);
  const fullWeeks = $derived(load.weeks.slice(0, -1).filter((week) => week.load > 0));
  const lastWeek = $derived(fullWeeks.at(-1) ?? null);
  const weekLabels = $derived(load.weeks.map((week) => dayMonth(week.week)));

  const acwrStatus = (ratio: number | null): { status: string; label: string } => {
    if (ratio === null) return { status: "unknown", label: "sem dado" };
    if (ratio < 0.8) return { status: "attention", label: "abaixo da faixa ideal: destreinando" };
    if (ratio <= 1.3) return { status: "good", label: "faixa ideal" };
    if (ratio <= 1.5) return { status: "attention", label: "acima da faixa ideal" };
    return { status: "bad", label: "risco alto de lesão" };
  };
  const formStatus = (form: number | null): { status: string; label: string } => {
    if (form === null) return { status: "unknown", label: "sem dado" };
    if (form > 5) return { status: "good", label: "descansado" };
    if (form >= -10) return { status: "typical", label: "neutro" };
    if (form >= -30) return { status: "attention", label: "cansaço produtivo" };
    return { status: "bad", label: "cansaço excessivo" };
  };
  const monotonyStatus = (value: number | null): { status: string; label: string } => {
    if (value === null) return { status: "unknown", label: "sem dado" };
    if (value < 1.5) return { status: "good", label: "variado" };
    if (value < 2) return { status: "attention", label: "repetitivo" };
    return { status: "bad", label: "muito repetitivo" };
  };
</script>

<PageFrame
  title="Carga"
  description="Se você está treinando demais ou de menos, e se o treino tem a mistura certa de leve e forte. Conta corrida, futebol e academia que forem registrados no relógio."
>
  <div class="stats stats-vertical border border-base-content/10 bg-base-100 sm:stats-horizontal">
    <div class="stat">
      <div class="stat-title">Aguda ÷ crônica (Garmin)</div>
      <div class="stat-value text-2xl tabular-nums">{number(lastGarmin?.acwr ?? null, 1)}</div>
      <div class="stat-desc"><StatusText {...acwrStatus(lastGarmin?.acwr ?? null)} /></div>
    </div>
    <div class="stat">
      <div class="stat-title">Frescor hoje</div>
      <div class="stat-value text-2xl tabular-nums">{delta(today?.form ?? null)}</div>
      <div class="stat-desc"><StatusText {...formStatus(today?.form ?? null)} /></div>
    </div>
    <div class="stat">
      <div class="stat-title">Leve na última semana</div>
      <div class="stat-value text-2xl tabular-nums">
        {lastWeek?.easy_pct === null || !lastWeek ? "—" : `${number(lastWeek.easy_pct)}%`}
      </div>
      <div class="stat-desc">{lastWeek?.verdict ?? "sem treino"} · meta 80%</div>
    </div>
    <div class="stat">
      <div class="stat-title">Monotonia da última semana</div>
      <div class="stat-value text-2xl tabular-nums">{number(lastWeek?.monotony ?? null, 1)}</div>
      <div class="stat-desc"><StatusText {...monotonyStatus(lastWeek?.monotony ?? null)} /></div>
    </div>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="aguda">
    <div class="card-body gap-3 p-5">
      <h2 id="aguda" class="text-base font-semibold">Carga aguda e a faixa ótima</h2>
      <p class="text-xs text-base-content/70">
        Os números da Garmin. Carga aguda é a soma ponderada dos últimos 7 dias; a faixa sombreada é
        onde ela deveria ficar para você evoluir sem exagero, calculada a partir da carga crônica (4
        semanas).
      </p>
      <TimeChart
        series={[
          {
            label: "Aguda",
            points: load.days.map((day) => ({ date: day.date, value: day.acute })),
            slot: 0,
          },
          {
            label: "Crônica",
            points: load.days.map((day) => ({ date: day.date, value: day.chronic })),
            slot: 6,
            dashed: true,
          },
        ]}
        band={{
          label: "Faixa ótima",
          low: load.days.map((day) => ({ date: day.date, value: day.chronic_min })),
          high: load.days.map((day) => ({ date: day.date, value: day.chronic_max })),
          slot: 2,
        }}
        format={(value) => number(value)}
        ariaLabel="Carga aguda, crônica e faixa ótima"
      />
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="frescor">
    <div class="card-body gap-3 p-5">
      <h2 id="frescor" class="text-base font-semibold">Condicionamento, fadiga e frescor</h2>
      <p class="text-xs text-base-content/70">
        Calculados aqui a partir da carga de cada atividade. Condicionamento é a média de 42 dias,
        fadiga a de 7 dias; frescor é a diferença. Negativo moderado (−10 a −30) é o cansaço que faz
        evoluir; muito negativo pede descanso; positivo é bom para prova. Os primeiros 42 dias ainda
        estão estabilizando.
      </p>
      <TimeChart
        series={[
          {
            label: "Condicionamento",
            points: load.days.map((day) => ({ date: day.date, value: day.fitness })),
            slot: 0,
          },
          {
            label: "Fadiga",
            points: load.days.map((day) => ({ date: day.date, value: day.fatigue })),
            slot: 1,
          },
        ]}
        format={(value) => number(value)}
        ariaLabel="Condicionamento e fadiga"
        height="h-52"
      />
      <BarChart
        labels={load.days.map((day) => dayMonth(day.date))}
        series={[{ label: "Frescor", values: load.days.map((day) => day.form), slot: 2 }]}
        format={(value) => number(value)}
        signedColors
        height="h-36"
        ariaLabel="Frescor por dia"
      />
    </div>
  </section>

  <div class="grid gap-4 xl:grid-cols-2">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="intensidade">
      <div class="card-body gap-3 p-5">
        <h2 id="intensidade" class="text-base font-semibold">Leve × forte por semana</h2>
        <p class="text-xs text-base-content/70">
          Minutos por zona de FC. A regra 80/20: uns 80% do tempo leve (zonas 1–2) e 20% moderado ou
          forte.
        </p>
        <BarChart
          labels={weekLabels}
          series={[
            { label: "Leve (Z1–Z2)", values: load.weeks.map((week) => week.easy_min), slot: 2 },
            {
              label: "Moderado (Z3)",
              values: load.weeks.map((week) => week.moderate_min),
              slot: 3,
            },
            { label: "Forte (Z4–Z5)", values: load.weeks.map((week) => week.hard_min), slot: 1 },
          ]}
          stacked
          format={(value) => `${number(value)} min`}
          extraTooltip={(index) => {
            const week = load.weeks[index];
            return week?.easy_pct === null || !week
              ? []
              : [`${number(week.easy_pct)}% leve · ${week.verdict}`];
          }}
          ariaLabel="Minutos por intensidade por semana"
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="esportes">
      <div class="card-body gap-3 p-5">
        <h2 id="esportes" class="text-base font-semibold">Minutos por esporte</h2>
        <p class="text-xs text-base-content/70">
          Futebol e academia só aparecem quando a atividade é gravada no relógio.
        </p>
        <BarChart
          labels={weekLabels}
          series={[
            { label: "Corrida", values: load.weeks.map((week) => week.minutes_run), slot: 0 },
            { label: "Futebol", values: load.weeks.map((week) => week.minutes_football), slot: 2 },
            { label: "Academia", values: load.weeks.map((week) => week.minutes_gym), slot: 6 },
            { label: "Outros", values: load.weeks.map((week) => week.minutes_other), slot: 3 },
          ]}
          stacked
          format={(value) => `${number(value)} min`}
          extraTooltip={(index) => {
            const week = load.weeks[index];
            return week ? [`${number(week.km, 1)} km em ${week.runs} corrida(s)`] : [];
          }}
          ariaLabel="Minutos por esporte por semana"
        />
      </div>
    </section>
  </div>

  <div class="grid gap-4 xl:grid-cols-2">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="foco">
      <div class="card-body gap-3 p-5">
        <h2 id="foco" class="text-base font-semibold">Foco da carga nas últimas 4 semanas</h2>
        <p class="text-xs text-base-content/70">
          Como a Garmin divide a sua carga por tipo de esforço, e o equilíbrio que ela recomenda
          para você.
        </p>
        <FocusBars rows={load.focus} />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="monotonia">
      <div class="card-body gap-3 p-5">
        <h2 id="monotonia" class="text-base font-semibold">Monotonia e tensão</h2>
        <p class="text-xs text-base-content/70">
          Monotonia é a carga média do dia dividida pela variação entre os dias da semana: treinar
          igual todo dia aumenta o risco de lesão e doença. Tensão é a carga da semana vezes a
          monotonia.
        </p>
        <BarChart
          labels={weekLabels}
          series={[{ label: "Tensão", values: load.weeks.map((week) => week.strain), slot: 6 }]}
          format={(value) => number(value)}
          extraTooltip={(index) => {
            const week = load.weeks[index];
            return week?.monotony === null || !week
              ? []
              : [`monotonia ${number(week.monotony, 2)}`];
          }}
          height="h-48"
          ariaLabel="Tensão por semana"
        />
      </div>
    </section>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="calendario">
    <div class="card-body gap-3 p-5">
      <h2 id="calendario" class="text-base font-semibold">Calendário de treinos</h2>
      <TrainingCalendar days={load.calendar} />
    </div>
  </section>
</PageFrame>
