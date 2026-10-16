<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { SegmentedControl, Select } from "@viniaraujo68/plinth/components";
  import BarChart from "$lib/components/BarChart.svelte";
  import GlanceGrid from "$lib/components/GlanceGrid.svelte";
  import Hypnogram from "$lib/components/Hypnogram.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import SleepWindows from "$lib/components/SleepWindows.svelte";
  import StatusText from "$lib/components/StatusText.svelte";
  import TimeChart from "$lib/components/TimeChart.svelte";
  import type { RecoveryTrend } from "$lib/data/types";
  import { date, dayMonth, delta, hours, number } from "$lib/format";

  import type { Recovery, SleepNight } from "$lib/data/types";

  const { data }: { data: { recovery: Recovery; night: SleepNight | null; today: string } } =
    $props();
  const recovery = $derived(data.recovery);

  type Period = "4" | "12" | "26" | "52";
  let period = $state<Period>("12");

  const SLEEP_FEEDBACK: Record<string, string> = {
    NEGATIVE_NOT_RESTORATIVE: "pouco reparador",
    NEGATIVE_NOT_ENOUGH_REM: "pouco REM",
    NEGATIVE_LONG_BUT_NOT_ENOUGH_REM: "longo, mas pouco REM",
    NEGATIVE_SHORT: "curto",
    NEGATIVE_LATE_BED_TIME: "dormiu tarde",
    POSITIVE_LONG_AND_DEEP: "longo e profundo",
    POSITIVE_DEEP: "profundo",
    POSITIVE_RESTFUL: "reparador",
    POSITIVE_CONTINUOUS: "contínuo",
  };

  const windowed = (trend: RecoveryTrend) => {
    const end = trend.points.at(-1)?.date ?? "";
    const cutoff = new Date(Date.parse(`${end}T12:00:00Z`) - Number(period) * 7 * 86_400_000)
      .toISOString()
      .slice(0, 10);
    return trend.points.filter((point) => point.date > cutoff);
  };

  const summary = (trend: RecoveryTrend) => {
    const points = windowed(trend).filter((point) => point.value !== null) as {
      date: string;
      value: number;
    }[];
    const current = points.at(-1) ?? null;
    const average = points.length
      ? points.reduce((sum, point) => sum + point.value, 0) / points.length
      : null;
    const lowest = points.reduce<{ date: string; value: number } | null>(
      (best, point) => (!best || point.value < best.value ? point : best),
      null,
    );
    const highest = points.reduce<{ date: string; value: number } | null>(
      (best, point) => (!best || point.value > best.value ? point : best),
      null,
    );
    const difference = current && average !== null ? current.value - average : null;
    let status = "typical";
    if (difference !== null && trend.higher_is_better !== null && average) {
      const relative = difference / Math.abs(average);
      const better = trend.higher_is_better ? relative : -relative;
      if (better > 0.05) status = "good";
      else if (better < -0.15) status = "bad";
      else if (better < -0.05) status = "attention";
    }
    return { current, average, lowest, highest, difference, status };
  };

  const digitsOf = (trend: RecoveryTrend): 0 | 1 | 2 =>
    Math.min(2, Math.max(0, trend.digits)) as 0 | 1 | 2;
  const nightOptions = $derived(
    [...recovery.nights].reverse().map((night) => ({
      value: night.date,
      label: `${date(night.date)} · ${number(night.score)} · ${hours((night.sleep_h ?? 0) * 3600)}`,
    })),
  );
  let selectedNight = $derived(data.night?.date ?? null);
  const nightsChart = $derived(recovery.nights.slice(-Number(period) * 7));
</script>

<PageFrame
  title="Recuperação"
  description="Se o seu corpo está absorvendo o treino: VFC, FC de repouso, sono e energia comparados com o seu próprio normal."
>
  {#snippet header()}
    <div class="mt-2">
      <SegmentedControl
        options={[
          { id: "4", label: "4 semanas" },
          { id: "12", label: "12 semanas" },
          { id: "26", label: "26 semanas" },
          { id: "52", label: "52 semanas" },
        ]}
        bind:value={period}
        label="Período"
        caption="Período"
        size="sm"
      />
    </div>
  {/snippet}

  <section class="grid gap-3 md:grid-cols-2 xl:grid-cols-3" aria-label="Tendências">
    {#each recovery.trends as trend (trend.key)}
      {@const info = summary(trend)}
      {@const points = windowed(trend)}
      <article class="card border border-base-content/10 bg-base-100">
        <div class="card-body gap-2 p-4">
          <div class="flex items-baseline justify-between gap-2">
            <h2 class="font-semibold">{trend.label}</h2>
            <span class="text-xl font-semibold tabular-nums"
              >{number(info.current?.value ?? null, digitsOf(trend))}
              <span class="text-xs font-normal text-base-content/60">{trend.unit}</span></span
            >
          </div>
          <div class="flex flex-wrap items-center justify-between gap-2 text-xs">
            <StatusText
              status={info.status}
              label="{delta(info.difference, digitsOf(trend))} vs média do período ({number(
                info.average,
                digitsOf(trend),
              )})"
            />
            <span class="text-base-content/60 tabular-nums">
              mín {number(info.lowest?.value ?? null, digitsOf(trend))}{info.lowest
                ? ` (${dayMonth(info.lowest.date)})`
                : ""} · máx {number(info.highest?.value ?? null, digitsOf(trend))}{info.highest
                ? ` (${dayMonth(info.highest.date)})`
                : ""}
            </span>
          </div>
          <TimeChart
            series={[
              {
                label: "Dia",
                points: points.map((point) => ({ date: point.date, value: point.value })),
                slot: 0,
                line: false,
                dots: true,
              },
              {
                label: "Média de 7 dias",
                points: points.map((point) => ({ date: point.date, value: point.mean7 })),
                slot: 0,
                width: 2.5,
              },
            ]}
            band={trend.key === "hrv_last_night"
              ? {
                  label: "Sua faixa normal",
                  low: points.map((point) => ({ date: point.date, value: point.band_low })),
                  high: points.map((point) => ({ date: point.date, value: point.band_high })),
                  slot: 2,
                }
              : undefined}
            format={(value) => number(value, digitsOf(trend))}
            ariaLabel="{trend.label} por dia"
            legend={false}
            zero={false}
            height="h-40"
          />
          <p class="text-xs text-base-content/60">{trend.help}</p>
        </div>
      </article>
    {/each}
  </section>

  <div class="grid gap-4 xl:grid-cols-2">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="fases">
      <div class="card-body gap-3 p-5">
        <h2 id="fases" class="text-base font-semibold">Fases do sono por noite</h2>
        <p class="text-xs text-base-content/70">
          Horas em cada fase. Profundo recupera o corpo; REM consolida memória e aprendizado e se
          concentra no fim da noite.
        </p>
        <BarChart
          labels={nightsChart.map((night) => dayMonth(night.date))}
          series={[
            { label: "Profundo", values: nightsChart.map((night) => night.deep_h), slot: 0 },
            { label: "REM", values: nightsChart.map((night) => night.rem_h), slot: 2 },
            { label: "Leve", values: nightsChart.map((night) => night.light_h), slot: 4 },
            { label: "Acordado", values: nightsChart.map((night) => night.awake_h), slot: 3 },
          ]}
          stacked
          format={(value) => hours(value * 3600)}
          extraTooltip={(index) => {
            const night = nightsChart[index];
            return night
              ? [
                  `pontuação ${number(night.score)} · precisava de ${hours((night.need_h ?? 0) * 3600)}`,
                ]
              : [];
          }}
          ariaLabel="Fases do sono por noite"
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="regularidade">
      <div class="card-body gap-3 p-5">
        <h2 id="regularidade" class="text-base font-semibold">Regularidade do sono</h2>
        <p class="text-xs text-base-content/70">
          Cada barra vai da hora em que você dormiu até a hora em que acordou; a cor é a pontuação
          (mais escuro = melhor). Horários regulares ajudam a recuperação tanto quanto dormir mais.
        </p>
        <SleepWindows nights={nightsChart} />
      </div>
    </section>
  </div>

  {#if data.night}
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="noite">
      <div class="card-body gap-3 p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 id="noite" class="text-base font-semibold">A noite em detalhe</h2>
            <p class="text-xs text-base-content/70">
              Dormiu {data.night.night.bedtime ?? "—"}, acordou {data.night.night.wake_time ?? "—"} ·
              {hours((data.night.night.sleep_h ?? 0) * 3600)} · pontuação {number(
                data.night.night.score,
              )}
              {#if data.night.night.feedback}· {SLEEP_FEEDBACK[data.night.night.feedback] ??
                  data.night.night.feedback.toLowerCase().replaceAll("_", " ")}{/if}
            </p>
          </div>
          <div class="w-72 max-w-full">
            <Select
              options={nightOptions}
              bind:value={selectedNight}
              placeholder="Escolha uma noite"
              onchange={(value: string | null) => {
                if (value)
                  void goto(resolve("/recuperacao/[noite]", { noite: value }), {
                    noScroll: true,
                    keepFocus: true,
                  });
              }}
            />
          </div>
        </div>
        <Hypnogram night={data.night} />
      </div>
    </section>
  {/if}

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="mes">
    <div class="card-body gap-3 p-5">
      <h2 id="mes" class="text-base font-semibold">Mês num relance</h2>
      <p class="text-xs text-base-content/70">
        Cada dia comparado com os 28 dias anteriores. Verde: melhor que o seu normal; amarelo: pior;
        vermelho: bem pior. Passe o mouse para ver quantos desvios.
      </p>
      <GlanceGrid
        days={recovery.glance.slice(-35)}
        labels={recovery.glance_labels}
        today={data.today}
      />
    </div>
  </section>
</PageFrame>
