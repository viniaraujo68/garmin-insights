<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { Combobox } from "@viniaraujo68/plinth/components";
  import BaselineTileCard from "$lib/components/BaselineTileCard.svelte";
  import DayDetail from "$lib/components/DayDetail.svelte";
  import IllnessCard from "$lib/components/IllnessCard.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import ReadinessHero from "$lib/components/ReadinessHero.svelte";
  import SignalCard from "$lib/components/SignalCard.svelte";
  import WeekStrip from "$lib/components/WeekStrip.svelte";
  import type { ActivitySummary, Intraday, Meta, Today } from "$lib/data/types";
  import { date, datetime, dayTitle, km, number, pace, weekdayShort } from "$lib/format";
  import { labelOf, SPORT, TRAINING_EFFECT } from "$lib/labels";

  const {
    data,
  }: {
    data: {
      meta: Meta;
      today: Today;
      intraday: Intraday | null;
      lastActivity: ActivitySummary | null;
      previousDay: string | null;
      nextDay: string | null;
    };
  } = $props();
  const today = $derived(data.today);
  const last = $derived(data.lastActivity);
  const isLatest = $derived(data.nextDay === null);
  const dayOptions = $derived(
    [...data.meta.days]
      .reverse()
      .map((day) => ({ value: day, label: `${weekdayShort(day)} ${date(day)}` })),
  );
  let chosenDay = $derived<string | null>(data.today.date);
  const openDay = (day: string | null): void => {
    if (day && day !== data.today.date)
      void goto(resolve("/day/[date]", { date: day }), { noScroll: true, keepFocus: true });
  };
</script>

<PageFrame
  title={isLatest ? "Today" : dayTitle(today.date)}
  description="How you woke up, what changed from your normal and how the week has been."
>
  {#snippet header()}
    <p class="text-xs text-base-content/60">
      {isLatest ? `${dayTitle(today.date)} · ` : ""}data from {datetime(data.meta.generated_at)}
    </p>
    <nav class="mt-2 flex flex-wrap items-center gap-2" aria-label="Choose the day">
      {#if data.previousDay}
        <a class="btn btn-ghost btn-sm" href={resolve("/day/[date]", { date: data.previousDay })}
          >← previous day</a
        >
      {/if}
      <div class="w-56">
        <Combobox
          options={dayOptions}
          bind:value={chosenDay}
          placeholder="Choose a day"
          emptyLabel="No day matches"
          aria-label="Day"
          onchange={openDay}
        />
      </div>
      {#if data.nextDay}
        <a class="btn btn-ghost btn-sm" href={resolve("/day/[date]", { date: data.nextDay })}
          >next day →</a
        >
        <a class="btn btn-ghost btn-sm" href={resolve("/")}>today</a>
      {/if}
    </nav>
  {/snippet}

  <ReadinessHero readiness={today.readiness} trainingStatus={today.training_status} />

  <section aria-labelledby="now" class="flex flex-col gap-3">
    <h2 id="now" class="text-base font-semibold">Compared with your normal</h2>
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {#each today.tiles as tile (tile.key)}
        <BaselineTileCard {tile} />
      {/each}
    </div>
  </section>

  {#if data.intraday}
    <DayDetail day={data.intraday} partial={isLatest} />
  {/if}

  <IllnessCard watch={today.illness} />

  <section aria-labelledby="week" class="card border border-base-content/10 bg-base-100">
    <div class="card-body gap-4 p-5">
      <h2 id="week" class="text-base font-semibold">Last 7 days</h2>
      <WeekStrip week={today.week} />
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {#each today.signals as signal (signal.key)}
          <SignalCard {signal} />
        {/each}
      </div>
    </div>
  </section>

  {#if last}
    <a
      href={last.sport === "run" ? resolve("/runs/[id]", { id: last.activity_id }) : undefined}
      class="card border border-base-content/10 bg-base-100 transition-colors hover:border-base-content/30"
    >
      <div class="card-body gap-2 p-5">
        <h2 class="text-base font-semibold">
          Last activity · {SPORT[last.sport] ?? last.sport}
        </h2>
        <div class="flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <span
            ><span class="text-base-content/60">Distance</span>
            <b class="tabular-nums">{km(last.distance_km, 2)}</b></span
          >
          {#if last.pace_s_km}<span
              ><span class="text-base-content/60">Pace</span>
              <b class="tabular-nums">{pace(last.pace_s_km)}/km</b></span
            >{/if}
          <span
            ><span class="text-base-content/60">Avg HR</span>
            <b class="tabular-nums">{number(last.avg_hr)} bpm</b></span
          >
          <span
            ><span class="text-base-content/60">Load</span>
            <b class="tabular-nums">{number(last.training_load)}</b></span
          >
          <span
            ><span class="text-base-content/60">Type</span>
            <b>{labelOf(TRAINING_EFFECT, last.training_effect_label)}</b></span
          >
          <span
            ><span class="text-base-content/60">Aerobic Training Effect</span>
            <b class="tabular-nums">{number(last.aerobic_te, 1)}</b></span
          >
        </div>
      </div>
    </a>
  {/if}
</PageFrame>
