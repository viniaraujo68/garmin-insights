<script lang="ts">
  import {
    nearestPoint,
    niceScale,
    type LaneBand,
    type LaneMarker,
    type LanePoint,
    type LaneReference,
    type LaneSpan,
    type LaneTick,
  } from "$lib/lanes";

  let {
    points,
    secondary = [],
    xDomain,
    xTicks,
    format,
    tickFormat,
    color,
    label,
    yDomain = null,
    reverse = false,
    area = false,
    references = [],
    bands = [],
    markers = [],
    spans = [],
    barWidth = null,
    showXLabels = false,
    hover = $bindable(null),
    height = 72,
  }: {
    points: LanePoint[];
    secondary?: LanePoint[];
    xDomain: [number, number];
    xTicks: LaneTick[];
    format: (value: number) => string;
    tickFormat?: (value: number) => string;
    color: string;
    label: string;
    yDomain?: [number, number] | null;
    reverse?: boolean;
    area?: boolean;
    references?: LaneReference[];
    bands?: LaneBand[];
    markers?: LaneMarker[];
    spans?: LaneSpan[];
    barWidth?: number | null;
    showXLabels?: boolean;
    hover?: number | null;
    height?: number;
  } = $props();

  const LEFT = 44;
  const RIGHT = 8;
  const TOP = 6;
  const BOTTOM_LABELS = 18;

  let width = $state(600);
  const plotBottom = $derived(height - 4);
  const totalHeight = $derived(height + (showXLabels ? BOTTOM_LABELS : 0));
  const present = $derived(
    [...points, ...secondary]
      .map((point) => point.y)
      .concat(references.map((reference) => reference.y))
      .filter((value): value is number => value !== null),
  );
  const scale = $derived.by(() => {
    if (yDomain) return niceScale(yDomain[0], yDomain[1], 4);
    if (!present.length) return niceScale(0, 1);
    const sorted = [...present].sort((a, b) => a - b);
    const low = sorted[Math.floor(sorted.length * 0.02)] ?? 0;
    const high = sorted[Math.ceil(sorted.length * 0.98) - 1] ?? 1;
    return niceScale(low, high);
  });
  const domain = $derived(yDomain ?? scale.domain);
  const x = (value: number): number =>
    LEFT +
    ((value - xDomain[0]) / Math.max(1e-9, xDomain[1] - xDomain[0])) * (width - LEFT - RIGHT);
  const y = (value: number): number => {
    const ratio = (value - domain[0]) / Math.max(1e-9, domain[1] - domain[0]);
    const clamped = Math.min(1, Math.max(0, reverse ? 1 - ratio : ratio));
    return plotBottom - clamped * (plotBottom - TOP);
  };
  const yTicks = $derived.by(() => {
    const inside = scale.ticks.filter(
      (tick) => tick >= domain[0] - 1e-9 && tick <= domain[1] + 1e-9,
    );
    return inside.length > 4 ? inside.filter((_, index) => index % 2 === 0) : inside;
  });
  const path = (series: LanePoint[]): string => {
    let d = "";
    let pen = false;
    for (const point of series) {
      if (point.y === null) {
        pen = false;
        continue;
      }
      d += `${pen ? "L" : "M"}${x(point.x).toFixed(1)},${y(point.y).toFixed(1)}`;
      pen = true;
    }
    return d;
  };
  const line = $derived(path(points));
  const shade = $derived.by(() => {
    if (!area) return null;
    const segments: LanePoint[][] = [];
    let current: LanePoint[] = [];
    for (const point of points) {
      if (point.y === null) {
        if (current.length) segments.push(current);
        current = [];
        continue;
      }
      current.push(point);
    }
    if (current.length) segments.push(current);
    return segments
      .filter((segment) => segment.length > 1)
      .map((segment) => {
        const first = segment[0]!;
        const last = segment[segment.length - 1]!;
        return `${path(segment)}L${x(last.x).toFixed(1)},${plotBottom}L${x(first.x).toFixed(1)},${plotBottom}Z`;
      })
      .join("");
  });
  const tickAnchor = (value: number): "start" | "middle" | "end" => {
    if (x(value) > width - RIGHT - 16) return "end";
    if (x(value) < LEFT + 16) return "start";
    return "middle";
  };
  const visibleBands = $derived(bands.filter((band) => Math.abs(y(band.from) - y(band.to)) >= 6));
  const referenceLabelY = (value: number): number =>
    y(value) - TOP < 12 ? y(value) + 10 : y(value) - 3;
  const hovered = $derived(hover === null ? null : nearestPoint(points, hover));

  const onMove = (event: PointerEvent): void => {
    const box = (event.currentTarget as SVGElement).getBoundingClientRect();
    const ratio = (event.clientX - box.left - LEFT) / Math.max(1, box.width - LEFT - RIGHT);
    hover = xDomain[0] + Math.min(1, Math.max(0, ratio)) * (xDomain[1] - xDomain[0]);
  };
</script>

<div bind:clientWidth={width} class="w-full">
  <svg
    {width}
    height={totalHeight}
    class="block touch-none select-none"
    role="img"
    aria-label={label}
    onpointermove={onMove}
    onpointerleave={() => (hover = null)}
  >
    <rect
      x={LEFT}
      y={TOP}
      width={Math.max(0, width - LEFT - RIGHT)}
      height={plotBottom - TOP}
      class="fill-base-content/[0.03]"
    />
    {#each spans as span, index (index)}
      <rect
        x={x(span.from)}
        y={TOP}
        width={Math.max(1, x(span.to) - x(span.from))}
        height={plotBottom - TOP}
        fill={span.color}
        fill-opacity="0.14"
      />
      {#if span.label && x(span.to) - x(span.from) > 48}
        <text x={x(span.from) + 3} y={TOP + 10} class="fill-base-content/60 text-[9px]"
          >{span.label}</text
        >
      {/if}
    {/each}
    {#each visibleBands as band (band.from)}
      <rect
        x={LEFT}
        width={Math.max(0, width - LEFT - RIGHT)}
        y={Math.min(y(band.from), y(band.to))}
        height={Math.abs(y(band.from) - y(band.to))}
        fill={band.color}
        fill-opacity="0.09"
      />
      {#if band.label}
        <text
          x={width - RIGHT - 4}
          y={Math.min(y(band.from), y(band.to)) + 9}
          text-anchor="end"
          class="fill-base-content/40 text-[9px]">{band.label}</text
        >
      {/if}
    {/each}
    {#each xTicks as tick (tick.value)}
      <line
        x1={x(tick.value)}
        x2={x(tick.value)}
        y1={TOP}
        y2={plotBottom}
        class="stroke-base-content/10"
      />
      {#if showXLabels}
        <text
          x={x(tick.value)}
          y={totalHeight - 4}
          text-anchor={tickAnchor(tick.value)}
          class="fill-base-content/60 text-[10px] tabular-nums">{tick.label}</text
        >
      {/if}
    {/each}
    {#each yTicks as tick (tick)}
      <line x1={LEFT} x2={width - RIGHT} y1={y(tick)} y2={y(tick)} class="stroke-base-content/10" />
      <text
        x={LEFT - 6}
        y={y(tick)}
        dy="0.32em"
        text-anchor="end"
        class="fill-base-content/60 text-[10px] tabular-nums">{(tickFormat ?? format)(tick)}</text
      >
    {/each}
    {#each references as reference (reference.y)}
      <line
        x1={LEFT}
        x2={width - RIGHT}
        y1={y(reference.y)}
        y2={y(reference.y)}
        class="stroke-base-content/35"
        stroke-dasharray="4 4"
      />
      <text
        x={width - RIGHT - 4}
        y={referenceLabelY(reference.y)}
        text-anchor="end"
        class="fill-base-content/50 text-[9px]">{reference.label}</text
      >
    {/each}
    {#each markers as marker (marker.x)}
      <line
        x1={x(marker.x)}
        x2={x(marker.x)}
        y1={TOP}
        y2={plotBottom}
        class="stroke-warning"
        stroke-dasharray="3 3"
      />
      <text x={x(marker.x) + 4} y={TOP + 10} class="fill-warning text-[9px] font-medium"
        >{marker.label}</text
      >
    {/each}
    {#if shade}<path d={shade} fill={color} fill-opacity="0.16" />{/if}
    {#if secondary.length}
      <path
        d={path(secondary)}
        fill="none"
        stroke={color}
        stroke-opacity="0.45"
        stroke-dasharray="3 3"
        stroke-width="1.2"
      />
    {/if}
    {#if barWidth === null}
      <path
        d={line}
        fill="none"
        stroke={color}
        stroke-width="1.8"
        stroke-linejoin="round"
        stroke-linecap="round"
      />
    {:else}
      {#each points as point (point.x)}
        {#if point.y !== null && point.y > 0}
          <rect
            x={x(point.x - barWidth / 2) + 0.5}
            y={y(point.y)}
            width={Math.max(1, x(point.x + barWidth / 2) - x(point.x - barWidth / 2) - 1)}
            height={Math.max(0, plotBottom - y(point.y))}
            fill={color}
            fill-opacity={hovered === point ? 1 : 0.75}
          />
        {/if}
      {/each}
    {/if}
    {#if hover !== null}
      <line x1={x(hover)} x2={x(hover)} y1={TOP} y2={plotBottom} class="stroke-base-content/60" />
      {#if hovered && hovered.y !== null && barWidth === null}
        <circle
          cx={x(hovered.x)}
          cy={y(hovered.y)}
          r="3.5"
          fill={color}
          class="stroke-base-100"
          stroke-width="1.5"
        />
      {/if}
    {/if}
  </svg>
</div>
