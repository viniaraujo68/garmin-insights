<script lang="ts">
  import type { Night } from "$lib/data/types";
  import { dayMonth } from "$lib/format";

  const { nights }: { nights: Night[] } = $props();

  const START = 20 * 60;
  const END = 36 * 60;
  const HEIGHT = 220;
  const TOP = 8;
  const BOTTOM = 22;
  const LEFT = 40;
  const TICKS = [20, 22, 24, 26, 28, 30, 32, 34, 36];

  let available = $state(640);
  const rows = $derived(
    nights.filter((night) => night.bedtime_minutes !== null && night.wake_minutes !== null),
  );
  const width = $derived(Math.max(320, available));
  const step = $derived(Math.max(6, (width - LEFT) / Math.max(1, rows.length)));
  const labelEvery = $derived(Math.max(1, Math.ceil(56 / step)));

  const absolute = (minutesAfterEvening: number): number => 18 * 60 + minutesAfterEvening;
  const wakeAbsolute = (minutes: number): number =>
    minutes < 18 * 60 ? minutes + 24 * 60 : minutes;
  const y = (minutes: number): number =>
    TOP +
    ((Math.min(END, Math.max(START, minutes)) - START) / (END - START)) * (HEIGHT - TOP - BOTTOM);
  const label = (hour: number): string => `${String(hour % 24).padStart(2, "0")}h`;
  const tone = (score: number | null): string => {
    if (score === null) return "var(--color-base-300)";
    const pct = Math.round(Math.min(100, Math.max(0, ((score - 40) / 50) * 100)));
    return `color-mix(in oklab, var(--ramp-high) ${pct}%, var(--ramp-low))`;
  };
</script>

<div class="overflow-x-auto" bind:clientWidth={available}>
  <svg {width} height={HEIGHT} role="img" aria-label="Horário de dormir e acordar por noite">
    {#each TICKS as hour (hour)}
      <line
        x1={LEFT}
        x2={width}
        y1={y(hour * 60)}
        y2={y(hour * 60)}
        class="stroke-base-content/10"
      />
      <text x="0" y={y(hour * 60) + 3} class="fill-base-content/60 text-[10px]">{label(hour)}</text>
    {/each}
    {#each rows as night, index (night.date)}
      {@const top = y(absolute(night.bedtime_minutes ?? 0))}
      {@const bottom = y(wakeAbsolute(night.wake_minutes ?? 0))}
      <rect
        x={LEFT + index * step + step * 0.15}
        y={top}
        width={step * 0.7}
        height={Math.max(2, bottom - top)}
        rx={Math.min(4, step * 0.35)}
        style:fill={tone(night.score)}
      >
        <title
          >{dayMonth(night.date)}: dormiu {night.bedtime}, acordou {night.wake_time} · pontuação {night.score ??
            "—"}</title
        >
      </rect>
      {#if index % labelEvery === 0}
        <text
          x={LEFT + index * step + step / 2}
          y={HEIGHT - 6}
          text-anchor="middle"
          class="fill-base-content/60 text-[10px]">{dayMonth(night.date)}</text
        >
      {/if}
    {/each}
  </svg>
</div>
