<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { Combobox } from "@viniaraujo68/plinth/components";
  import BaselineTileCard from "$lib/components/BaselineTileCard.svelte";
  import IllnessCard from "$lib/components/IllnessCard.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import ReadinessHero from "$lib/components/ReadinessHero.svelte";
  import SignalCard from "$lib/components/SignalCard.svelte";
  import WeekStrip from "$lib/components/WeekStrip.svelte";
  import type { ActivitySummary, Meta, Today } from "$lib/data/types";
  import { date, datetime, dayTitle, km, number, pace, weekdayShort } from "$lib/format";
  import { labelOf, SPORT, TRAINING_EFFECT } from "$lib/labels";

  const {
    data,
  }: {
    data: {
      meta: Meta;
      today: Today;
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
      void goto(resolve("/dia/[data]", { data: day }), { noScroll: true, keepFocus: true });
  };
</script>

<PageFrame
  title={isLatest ? "Hoje" : dayTitle(today.date)}
  description="Como você acordou, o que mudou em relação ao seu normal e como estava a semana."
>
  {#snippet header()}
    <p class="text-xs text-base-content/60">
      {isLatest ? `${dayTitle(today.date)} · ` : ""}dados de {datetime(data.meta.generated_at)}
    </p>
    <nav class="mt-2 flex flex-wrap items-center gap-2" aria-label="Escolher o dia">
      {#if data.previousDay}
        <a class="btn btn-ghost btn-sm" href={resolve("/dia/[data]", { data: data.previousDay })}
          >← dia anterior</a
        >
      {/if}
      <div class="w-56">
        <Combobox
          options={dayOptions}
          bind:value={chosenDay}
          placeholder="Escolha um dia"
          emptyLabel="Nenhum dia com esse texto"
          aria-label="Dia"
          onchange={openDay}
        />
      </div>
      {#if data.nextDay}
        <a class="btn btn-ghost btn-sm" href={resolve("/dia/[data]", { data: data.nextDay })}
          >próximo dia →</a
        >
        <a class="btn btn-ghost btn-sm" href={resolve("/")}>hoje</a>
      {/if}
    </nav>
  {/snippet}

  <ReadinessHero readiness={today.readiness} trainingStatus={today.training_status} />

  <section aria-labelledby="agora" class="flex flex-col gap-3">
    <h2 id="agora" class="text-base font-semibold">Comparado com o seu normal</h2>
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {#each today.tiles as tile (tile.key)}
        <BaselineTileCard {tile} />
      {/each}
    </div>
  </section>

  <IllnessCard watch={today.illness} />

  <section aria-labelledby="semana" class="card border border-base-content/10 bg-base-100">
    <div class="card-body gap-4 p-5">
      <h2 id="semana" class="text-base font-semibold">Últimos 7 dias</h2>
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
      href={last.sport === "run" ? resolve("/corridas/[id]", { id: last.activity_id }) : undefined}
      class="card border border-base-content/10 bg-base-100 transition-colors hover:border-base-content/30"
    >
      <div class="card-body gap-2 p-5">
        <h2 class="text-base font-semibold">
          Última atividade · {SPORT[last.sport] ?? last.sport}
        </h2>
        <div class="flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <span
            ><span class="text-base-content/60">Distância</span>
            <b class="tabular-nums">{km(last.distance_km, 2)}</b></span
          >
          {#if last.pace_s_km}<span
              ><span class="text-base-content/60">Pace</span>
              <b class="tabular-nums">{pace(last.pace_s_km)}/km</b></span
            >{/if}
          <span
            ><span class="text-base-content/60">FC média</span>
            <b class="tabular-nums">{number(last.avg_hr)} bpm</b></span
          >
          <span
            ><span class="text-base-content/60">Carga</span>
            <b class="tabular-nums">{number(last.training_load)}</b></span
          >
          <span
            ><span class="text-base-content/60">Tipo</span>
            <b>{labelOf(TRAINING_EFFECT, last.training_effect_label)}</b></span
          >
          <span
            ><span class="text-base-content/60">Efeito aeróbico</span>
            <b class="tabular-nums">{number(last.aerobic_te, 1)}</b></span
          >
        </div>
      </div>
    </a>
  {/if}
</PageFrame>
