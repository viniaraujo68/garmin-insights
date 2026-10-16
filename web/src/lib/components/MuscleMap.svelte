<script lang="ts">
  import type { MuscleGroupSets } from "$lib/data/types";
  import { number } from "$lib/format";

  const { muscles, period }: { muscles: MuscleGroupSets[]; period: "7d" | "28d" } = $props();

  const value = (group: string): number => {
    const row = muscles.find((item) => item.group === group);
    if (!row) return 0;
    return period === "7d" ? row.sets_7d : row.sets_28d;
  };
  const max = $derived(
    Math.max(1, ...muscles.map((item) => (period === "7d" ? item.sets_7d : item.sets_28d))),
  );
  const fill = (group: string): string => {
    const sets = value(group);
    if (sets <= 0) return "color-mix(in srgb, var(--color-base-content) 8%, transparent)";
    return `color-mix(in oklab, var(--series-7) ${Math.round(25 + (sets / max) * 75)}%, var(--color-base-100))`;
  };
  const label = (group: string): string =>
    muscles.find((item) => item.group === group)?.label ?? group;
  const tip = (group: string): string => `${label(group)}: ${number(value(group), 1)} séries`;

  const FRONT = [
    { group: "shoulders", shape: "ellipse", cx: 52, cy: 62, rx: 11, ry: 9 },
    { group: "shoulders", shape: "ellipse", cx: 108, cy: 62, rx: 11, ry: 9 },
    { group: "chest", shape: "rect", x: 60, y: 62, width: 40, height: 26, rx: 8 },
    { group: "biceps", shape: "rect", x: 38, y: 74, width: 12, height: 32, rx: 6 },
    { group: "biceps", shape: "rect", x: 110, y: 74, width: 12, height: 32, rx: 6 },
    { group: "core", shape: "rect", x: 64, y: 92, width: 32, height: 44, rx: 8 },
    { group: "quads", shape: "rect", x: 60, y: 146, width: 18, height: 52, rx: 8 },
    { group: "quads", shape: "rect", x: 82, y: 146, width: 18, height: 52, rx: 8 },
  ];
  const BACK = [
    { group: "shoulders", shape: "ellipse", cx: 52, cy: 62, rx: 11, ry: 9 },
    { group: "shoulders", shape: "ellipse", cx: 108, cy: 62, rx: 11, ry: 9 },
    { group: "back", shape: "rect", x: 60, y: 58, width: 40, height: 56, rx: 10 },
    { group: "triceps", shape: "rect", x: 38, y: 74, width: 12, height: 32, rx: 6 },
    { group: "triceps", shape: "rect", x: 110, y: 74, width: 12, height: 32, rx: 6 },
    { group: "glutes", shape: "rect", x: 60, y: 120, width: 40, height: 24, rx: 10 },
    { group: "hamstrings", shape: "rect", x: 60, y: 148, width: 18, height: 42, rx: 8 },
    { group: "hamstrings", shape: "rect", x: 82, y: 148, width: 18, height: 42, rx: 8 },
    { group: "calves", shape: "rect", x: 62, y: 198, width: 14, height: 34, rx: 7 },
    { group: "calves", shape: "rect", x: 84, y: 198, width: 14, height: 34, rx: 7 },
  ];
  const OUTLINE =
    "M80 14a14 14 0 1 1 0 28 14 14 0 0 1 0-28Zm-22 38h44l14 8 8 52-8 2-8-40v34l2 4-4 4 2 56-4 64h-12l-4-62-4 62h-12l-4-64 2-56-4-4 2-4V68l-8 40-8-2 8-52Z";
</script>

<div class="flex flex-wrap items-start justify-center gap-6">
  {#each [{ title: "Frente", parts: FRONT }, { title: "Costas", parts: BACK }] as view (view.title)}
    <figure class="flex flex-col items-center gap-1">
      <svg
        viewBox="20 6 120 240"
        class="h-64 w-auto"
        role="img"
        aria-label="Músculos trabalhados, {view.title.toLowerCase()}"
      >
        <path d={OUTLINE} class="fill-base-content/5 stroke-base-content/20" stroke-width="1" />
        {#each view.parts as part, index (index)}
          {#if part.shape === "ellipse"}
            <ellipse
              cx={part.cx}
              cy={part.cy}
              rx={part.rx}
              ry={part.ry}
              style:fill={fill(part.group)}><title>{tip(part.group)}</title></ellipse
            >
          {:else}
            <rect
              x={part.x}
              y={part.y}
              width={part.width}
              height={part.height}
              rx={part.rx}
              style:fill={fill(part.group)}><title>{tip(part.group)}</title></rect
            >
          {/if}
        {/each}
      </svg>
      <figcaption class="text-xs text-base-content/60">{view.title}</figcaption>
    </figure>
  {/each}
  <ul class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
    {#each muscles as item (item.group)}
      <li class="flex items-center justify-between gap-3">
        <span class="inline-flex items-center gap-1.5"
          ><i class="size-2.5 rounded-sm" style:background={fill(item.group)}></i>{item.label}</span
        >
        <span class="tabular-nums">{number(period === "7d" ? item.sets_7d : item.sets_28d, 1)}</span
        >
      </li>
    {/each}
  </ul>
</div>
