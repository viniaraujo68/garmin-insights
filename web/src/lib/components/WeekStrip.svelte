<script lang="ts">
  import { resolve } from "$app/paths";
  import type { WeekDay } from "$lib/data/types";
  import { dayMonth, km, number, weekdayShort } from "$lib/format";
  import { SPORT } from "$lib/labels";

  const { week }: { week: WeekDay[] } = $props();

  const SPORT_VAR: Record<string, string> = {
    run: "var(--sport-run)",
    football: "var(--sport-football)",
    gym: "var(--sport-gym)",
    other: "var(--sport-other)",
  };
</script>

<ol class="grid grid-cols-7 gap-1.5">
  {#each week as day (day.date)}
    <li class="flex min-h-24 min-w-0 flex-col gap-1 rounded-box border border-base-content/10 p-2">
      <span class="text-[11px] text-base-content/60 capitalize"
        >{weekdayShort(day.date)} {dayMonth(day.date)}</span
      >
      {#each day.activities as activity (activity.activity_id)}
        <a
          href={activity.sport === "run"
            ? resolve("/corridas/[id]", { id: activity.activity_id })
            : undefined}
          class="block rounded-field px-1.5 py-1 text-[11px] leading-tight text-white"
          style:background={SPORT_VAR[activity.sport] ?? SPORT_VAR["other"]}
        >
          <span class="block truncate font-semibold">{SPORT[activity.sport] ?? activity.sport}</span
          >
          <span class="block tabular-nums"
            >{activity.distance_km
              ? km(activity.distance_km)
              : `${number(activity.duration_min)} min`}</span
          >
        </a>
      {:else}
        <span class="mt-auto text-[11px] text-base-content/30"
          ><span class="hidden sm:inline">descanso</span><span
            class="sm:hidden"
            aria-label="descanso">—</span
          ></span
        >
      {/each}
    </li>
  {/each}
</ol>
