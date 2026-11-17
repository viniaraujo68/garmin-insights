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
    good: "in range",
    attention: "below range",
    bad: "above range",
    unknown: "no data",
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
  const runsLabel = (runs: number): string => `${runs} ${runs === 1 ? "run" : "runs"}`;
</script>

<PageFrame
  title="Load"
  description="Whether you are training enough, too much or too little, and whether your mix of easy and hard is right."
>
  <section
    class="card border border-base-content/10 bg-base-100"
    aria-labelledby="verdict"
    data-testid="load-summary"
  >
    <div class="card-body gap-3 p-5">
      <StatusText status={summary.status} label={SUMMARY_LABEL[summary.status] ?? "no data"} />
      <h2 id="verdict" class="text-xl font-semibold tracking-tight">{summary.headline}</h2>
      <p class="max-w-3xl text-sm text-base-content/80">{summary.detail}</p>
      {#if summary.easy_line}
        <p class="max-w-3xl text-sm text-base-content/80">{summary.easy_line}</p>
      {/if}
    </div>
  </section>

  <div class="grid gap-4 xl:grid-cols-2">
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="volume">
      <div class="card-body gap-3 p-5">
        <h2 id="volume" class="text-base font-semibold">Kilometres per week</h2>
        <p class="text-xs text-base-content/70">
          How far you ran each week (Monday to Sunday). The week marked * is still in progress.
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
          ariaLabel="Kilometres per week"
        />
      </div>
    </section>
    <section class="card border border-base-content/10 bg-base-100" aria-labelledby="easy">
      <div class="card-body gap-3 p-5">
        <h2 id="easy" class="text-base font-semibold">How much of the time was easy</h2>
        <p class="text-xs text-base-content/70">
          % of running time in HR zones 1 and 2. The 80/20 rule: around 80% easy lets you handle
          more training and improve more. Well below the line = too hard.
        </p>
        <BarChart
          labels={weekLabels}
          series={[{ label: "Easy", values: weeks.map((week) => week.easy_pct), slot: 2 }]}
          format={(value) => `${number(value)}%`}
          reference={{ value: 80, label: "target 80%" }}
          extraTooltip={(index) => {
            const week = weeks[index];
            return week
              ? [
                  `${number(week.easy_min)} de ${number(week.easy_min + week.moderate_min + week.hard_min)} min easy`,
                ]
              : [];
          }}
          height="h-56"
          ariaLabel="Percentage of easy time per week"
        />
      </div>
    </section>
  </div>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="range">
    <div class="card-body gap-3 p-5">
      <h2 id="range" class="text-base font-semibold">Last 7 days load</h2>
      <p class="text-xs text-base-content/70">
        Each point adds up the effort (the load Garmin gives each workout) of the previous 7 days.
        The green band is how much you can handle, calculated from your last 4 weeks: inside it you
        improve; below it you are detraining; above it injury risk rises.
      </p>
      <TimeChart
        series={[
          {
            label: "Last 7 days load",
            points: garminDays.map((day) => ({ date: day.date, value: day.acute })),
            slot: 0,
            width: 2.5,
          },
        ]}
        band={{
          label: "Recommended range",
          low: garminDays.map((day) => ({ date: day.date, value: day.chronic_min })),
          high: garminDays.map((day) => ({ date: day.date, value: day.chronic_max })),
          slot: 2,
        }}
        format={(value) => number(value)}
        ariaLabel="Last 7 days load and recommended range"
        height="h-56"
      />
    </div>
  </section>
</PageFrame>
