<script lang="ts">
  import type { CalendarDay } from "$lib/data/types";
  import { dayMonth, number } from "$lib/format";
  import { SPORT } from "$lib/labels";

  const { days }: { days: CalendarDay[] } = $props();

  const CELL = 15;
  const GAP = 3;
  const WEEKDAYS = ["seg", "", "qua", "", "sex", "", "dom"];
  const MONTHS = [
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
  ];
  const SPORT_VAR: Record<string, string> = {
    run: "var(--sport-run)",
    football: "var(--sport-football)",
    gym: "var(--sport-gym)",
    other: "var(--sport-other)",
  };

  const weekdayOf = (day: string): number => (new Date(`${day}T12:00:00Z`).getUTCDay() + 6) % 7;
  const maxLoad = $derived(Math.max(1, ...days.map((day) => day.load)));
  const cells = $derived.by(() => {
    const offset = days.length ? weekdayOf(days[0]!.date) : 0;
    return days.map((day, index) => {
      const position = index + offset;
      return { ...day, column: Math.floor(position / 7), row: position % 7 };
    });
  });
  const columns = $derived(cells.length ? cells[cells.length - 1]!.column + 1 : 0);
  const months = $derived(
    cells
      .filter(
        (cell) =>
          cell.date.endsWith("-01") || (cell === cells[0] && Number(cell.date.slice(8, 10)) <= 20),
      )
      .map((cell) => ({
        column: cell.column,
        label: MONTHS[Number(cell.date.slice(5, 7)) - 1] ?? "",
      })),
  );
  const fill = (load: number): string =>
    load <= 0
      ? "color-mix(in srgb, var(--color-base-content) 6%, transparent)"
      : `color-mix(in oklab, var(--ramp-high) ${Math.round(20 + (load / maxLoad) * 80)}%, var(--ramp-low))`;
  const LEFT = 30;
  const TOP = 16;
</script>

<div class="overflow-x-auto">
  <svg
    width={LEFT + columns * (CELL + GAP)}
    height={TOP + 7 * (CELL + GAP)}
    role="img"
    aria-label="Calendário de treinos"
  >
    {#each months as month (month.column + month.label)}
      <text x={LEFT + month.column * (CELL + GAP)} y="10" class="fill-base-content/60 text-[10px]"
        >{month.label}</text
      >
    {/each}
    {#each WEEKDAYS as label, row (row)}
      {#if label}<text
          x="0"
          y={TOP + row * (CELL + GAP) + CELL - 3}
          class="fill-base-content/60 text-[10px]">{label}</text
        >{/if}
    {/each}
    {#each cells as cell (cell.date)}
      <rect
        x={LEFT + cell.column * (CELL + GAP)}
        y={TOP + cell.row * (CELL + GAP)}
        width={CELL}
        height={CELL}
        rx="3"
        style:fill={fill(cell.load)}
        style:stroke={cell.sports.length ? SPORT_VAR[cell.sports[0] ?? "other"] : "none"}
        stroke-width={cell.sports.length > 1 ? 2.5 : 1.5}
      >
        <title
          >{dayMonth(cell.date)} · {cell.sports.length
            ? cell.sports.map((sport) => SPORT[sport] ?? sport).join(" + ")
            : "descanso"} · carga {number(cell.load)}</title
        >
      </rect>
    {/each}
  </svg>
</div>
<div class="mt-2 flex flex-wrap items-center gap-4 text-xs text-base-content/70">
  <span class="inline-flex items-center gap-1.5"
    >menos carga
    {#each [0, 0.25, 0.5, 0.75, 1] as step (step)}<i
        class="size-3 rounded-[3px]"
        style:background={fill(step * maxLoad)}
      ></i>{/each}
    mais carga
  </span>
  {#each Object.entries(SPORT_VAR) as [sport, color] (sport)}
    <span class="inline-flex items-center gap-1.5"
      ><i class="size-3 rounded-[3px] border-2" style:border-color={color}></i>{SPORT[sport]}</span
    >
  {/each}
</div>
