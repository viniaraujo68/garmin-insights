<script lang="ts">
  import type { SparkPoint } from "$lib/data/types";
  import { dayMonth, number } from "$lib/format";
  import { niceScale } from "$lib/lanes";

  const {
    points,
    bandLow = null,
    bandHigh = null,
    unit = "",
    yDomain = null,
    label,
  }: {
    points: SparkPoint[];
    bandLow?: number | null;
    bandHigh?: number | null;
    unit?: string;
    yDomain?: [number, number] | null;
    label: string;
  } = $props();

  const LEFT = 30;
  const RIGHT = 6;
  const TOP = 6;
  const PLOT = 56;
  const HEIGHT = PLOT + 16;

  let width = $state(240);
  let hover = $state<number | null>(null);

  const present = $derived(
    points.map((point) => point.value).filter((value): value is number => value !== null),
  );
  const scale = $derived.by(() => {
    if (yDomain) return niceScale(yDomain[0], yDomain[1], 2);
    const all = [
      ...present,
      ...(bandLow === null ? [] : [bandLow]),
      ...(bandHigh === null ? [] : [bandHigh]),
    ];
    return niceScale(Math.min(...all), Math.max(...all), 2);
  });
  const x = (index: number): number =>
    LEFT + (index / Math.max(1, points.length - 1)) * (width - LEFT - RIGHT);
  const y = (value: number): number => {
    const [low, high] = scale.domain;
    return PLOT - ((value - low) / Math.max(1e-9, high - low)) * (PLOT - TOP);
  };
  const path = $derived(
    points
      .reduce<string[]>((parts, point, index) => {
        if (point.value === null) return parts;
        const previous = points[index - 1];
        const move = index === 0 || !previous || previous.value === null;
        parts.push(`${move ? "M" : "L"}${x(index).toFixed(1)},${y(point.value).toFixed(1)}`);
        return parts;
      }, [])
      .join(""),
  );
  const tickLabel = (value: number): string =>
    Math.abs(value) >= 10_000 ? `${number(value / 1000)}k` : number(value);
  const hovered = $derived(hover === null ? null : (points[hover] ?? null));
  const first = $derived(points[0]);
  const last = $derived(points[points.length - 1]);

  const onMove = (event: PointerEvent): void => {
    const box = (event.currentTarget as SVGElement).getBoundingClientRect();
    const ratio = (event.clientX - box.left - LEFT) / Math.max(1, box.width - LEFT - RIGHT);
    hover = Math.round(Math.min(1, Math.max(0, ratio)) * (points.length - 1));
  };
</script>

{#if present.length >= 2}
  <div bind:clientWidth={width} class="relative w-full">
    <svg
      {width}
      height={HEIGHT}
      class="block touch-none select-none"
      role="img"
      aria-label={label}
      onpointermove={onMove}
      onpointerleave={() => (hover = null)}
    >
      {#if bandLow !== null && bandHigh !== null}
        <rect
          x={LEFT}
          width={Math.max(0, width - LEFT - RIGHT)}
          y={y(bandHigh)}
          height={Math.max(1, y(bandLow) - y(bandHigh))}
          class="fill-success/15"
        />
      {/if}
      {#each scale.ticks as tick (tick)}
        <line
          x1={LEFT}
          x2={width - RIGHT}
          y1={y(tick)}
          y2={y(tick)}
          class="stroke-base-content/10"
        />
        <text
          x={LEFT - 5}
          y={y(tick)}
          dy="0.32em"
          text-anchor="end"
          class="fill-base-content/60 text-[10px] tabular-nums">{tickLabel(tick)}</text
        >
      {/each}
      <path
        d={path}
        fill="none"
        stroke="var(--series-1)"
        stroke-width="1.8"
        stroke-linejoin="round"
        stroke-linecap="round"
      />
      {#each points as point, index (point.date)}
        {#if point.value !== null}
          <circle
            cx={x(index)}
            cy={y(point.value)}
            r={index === points.length - 1 || index === hover ? 3.5 : 2}
            fill="var(--series-1)"
            class="stroke-base-100"
            stroke-width="1.5"
          />
        {/if}
      {/each}
      {#if hover !== null}
        <line x1={x(hover)} x2={x(hover)} y1={TOP} y2={PLOT} class="stroke-base-content/40" />
      {/if}
      {#if first && last}
        <text x={LEFT} y={HEIGHT - 3} class="fill-base-content/60 text-[10px] tabular-nums"
          >{dayMonth(first.date)}</text
        >
        <text
          x={width - RIGHT}
          y={HEIGHT - 3}
          text-anchor="end"
          class="fill-base-content/60 text-[10px] tabular-nums">{dayMonth(last.date)}</text
        >
      {/if}
    </svg>
    {#if hover !== null && hovered}
      <div
        class="pointer-events-none absolute top-0 z-10 rounded border border-base-content/10 bg-base-100 px-1.5 py-0.5 text-[11px] whitespace-nowrap tabular-nums shadow-sm"
        style:left="{Math.min(Math.max(x(hover), LEFT + 30), width - 40)}px"
        style:transform="translate(-50%, -110%)"
      >
        {dayMonth(hovered.date)} ·
        <b>{hovered.value === null ? "—" : `${number(hovered.value)}${unit ? ` ${unit}` : ""}`}</b>
      </div>
    {/if}
  </div>
{:else}
  <div class="h-18"></div>
{/if}
