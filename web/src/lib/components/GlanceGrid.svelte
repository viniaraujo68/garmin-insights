<script lang="ts">
  import type { GlanceDay } from "$lib/data/types";
  import { dayMonth, weekdayShort } from "$lib/format";

  const { days, labels, today }: { days: GlanceDay[]; labels: string[]; today: string } = $props();

  const TONE: Record<string, string> = {
    good: "bg-success/20 text-success",
    typical: "bg-base-content/5",
    attention: "bg-warning/25",
    bad: "bg-error/25 text-error",
    unknown: "text-base-content/40",
  };
</script>

<div class="overflow-x-auto">
  <table class="w-full border-separate border-spacing-1 text-xs tabular-nums">
    <thead>
      <tr>
        <th class="text-left font-medium text-base-content/60">Dia</th>
        {#each labels as label (label)}<th class="font-medium text-base-content/60">{label}</th
          >{/each}
      </tr>
    </thead>
    <tbody>
      {#each [...days].reverse() as day (day.date)}
        <tr>
          <th class="text-left font-normal whitespace-nowrap">
            <span class="text-base-content/60">{weekdayShort(day.date)}</span>
            {dayMonth(day.date)}{day.date === today ? " (parcial)" : ""}
          </th>
          {#each day.cells as cell (cell.key)}
            <td
              class={["rounded-field px-2 py-1 text-center", TONE[cell.status]]}
              title={cell.z === null
                ? "sem referência"
                : `${cell.z > 0 ? "+" : ""}${String(cell.z).replace(".", ",")} desvios do seu normal`}
              >{cell.display}</td
            >
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
