<script lang="ts">
  import type { Streams } from "$lib/data/types";
  import { delta, number, pace } from "$lib/format";
  import { nearestByDistance, smooth } from "$lib/streams";

  let { streams, hover = $bindable(null) }: { streams: Streams; hover?: number | null } = $props();

  interface Lane {
    key: string;
    label: string;
    values: (number | null)[];
    secondary?: (number | null)[];
    secondaryLabel?: string;
    format: (value: number | null) => string;
    reverse?: boolean;
    area?: boolean;
    zero?: boolean;
    color: string;
  }

  const WIDTH = 1000;
  const HEIGHT = 64;

  const present = (values: (number | null)[]): boolean => values.some((value) => value !== null);

  const lanes = $derived<Lane[]>(
    [
      {
        key: "pace",
        label: "Pace",
        values: smooth(streams.pace_s_km, 6),
        secondary: smooth(streams.gap_pace_s_km, 6),
        secondaryLabel: "ajustado à inclinação",
        format: (value: number | null) => `${pace(value)}/km`,
        reverse: true,
        color: "var(--series-1)",
      },
      {
        key: "hr",
        label: "FC",
        values: smooth(streams.hr, 2),
        format: (value: number | null) => `${number(value)} bpm`,
        color: "var(--series-8)",
      },
      {
        key: "cadence",
        label: "Cadência",
        values: smooth(streams.cadence, 4),
        format: (value: number | null) => `${number(value)} ppm`,
        color: "var(--series-7)",
      },
      {
        key: "power",
        label: "Potência",
        values: smooth(streams.power, 4),
        format: (value: number | null) => `${number(value)} W`,
        color: "var(--series-4)",
      },
      {
        key: "elevation",
        label: "Altitude",
        values: streams.elevation,
        format: (value: number | null) => `${number(value)} m`,
        area: true,
        color: "var(--series-3)",
      },
      {
        key: "condition",
        label: "Condição de desempenho",
        values: streams.performance_condition,
        format: (value: number | null) => delta(value),
        zero: true,
        color: "var(--series-2)",
      },
    ].filter((lane) => present(lane.values)),
  );

  const distances = $derived(streams.distance_m);
  const total = $derived(
    Math.max(1, ...distances.filter((value): value is number => value !== null)),
  );
  const x = (distance: number | null): number => ((distance ?? 0) / total) * WIDTH;

  const extent = (lane: Lane): [number, number] => {
    const all = [...lane.values, ...(lane.secondary ?? [])]
      .filter((value): value is number => value !== null)
      .sort((a, b) => a - b);
    let low = all[Math.floor(all.length * 0.02)] ?? 0;
    let high = all[Math.ceil(all.length * 0.98) - 1] ?? 1;
    if (lane.zero) {
      low = Math.min(low, -5);
      high = Math.max(high, 5);
    }
    return high === low ? [low - 1, high + 1] : [low, high];
  };

  const yOf =
    (lane: Lane, range: [number, number]) =>
    (value: number): number => {
      const ratio = (value - range[0]) / (range[1] - range[0]);
      const clamped = Math.min(1, Math.max(0, lane.reverse ? 1 - ratio : ratio));
      return HEIGHT - 4 - clamped * (HEIGHT - 8);
    };

  const path = (values: (number | null)[], y: (value: number) => number): string => {
    let d = "";
    let pen = false;
    values.forEach((value, index) => {
      const distance = distances[index];
      if (value === null || distance === null || distance === undefined) {
        pen = false;
        return;
      }
      d += `${pen ? "L" : "M"}${x(distance).toFixed(1)},${y(value).toFixed(1)}`;
      pen = true;
    });
    return d;
  };

  const drawn = $derived(
    lanes.map((lane) => {
      const range = extent(lane);
      const y = yOf(lane, range);
      const line = path(lane.values, y);
      const average = lane.values.filter((value): value is number => value !== null);
      return {
        lane,
        line,
        secondary: lane.secondary ? path(lane.secondary, y) : null,
        area: lane.area ? `${line}L${WIDTH},${HEIGHT}L0,${HEIGHT}Z` : null,
        zeroY: lane.zero ? y(0) : null,
        mean: average.length
          ? average.reduce((sum, value) => sum + value, 0) / average.length
          : null,
      };
    }),
  );

  const hoverX = $derived(hover === null ? null : x(distances[hover] ?? null));

  const onMove = (event: PointerEvent): void => {
    const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (event.clientX - box.left) / box.width));
    hover = nearestByDistance(distances, ratio * total);
  };
</script>

<div class="flex flex-col gap-1">
  {#each drawn as item (item.lane.key)}
    <div class="grid grid-cols-[7.5rem_1fr] items-center gap-3 sm:grid-cols-[10rem_1fr]">
      <div class="min-w-0 text-xs">
        <p class="truncate text-base-content/70">{item.lane.label}</p>
        <p class="text-sm font-semibold tabular-nums">
          {hover === null
            ? item.lane.format(item.mean)
            : item.lane.format(item.lane.values[hover] ?? null)}
        </p>
        {#if item.lane.secondary && hover !== null}
          <p class="truncate text-base-content/60 tabular-nums">
            {item.lane.format(item.lane.secondary[hover] ?? null)}
            {item.lane.secondaryLabel}
          </p>
        {:else if hover === null}
          <p class="text-base-content/50">média</p>
        {/if}
      </div>
      <svg
        viewBox="0 0 {WIDTH} {HEIGHT}"
        preserveAspectRatio="none"
        class="h-16 w-full touch-none"
        role="img"
        aria-label="{item.lane.label} ao longo da corrida"
        onpointermove={onMove}
        onpointerleave={() => (hover = null)}
      >
        <rect width={WIDTH} height={HEIGHT} class="fill-base-content/[0.03]" />
        {#if item.zeroY !== null}
          <line
            x1="0"
            x2={WIDTH}
            y1={item.zeroY}
            y2={item.zeroY}
            class="stroke-base-content/30"
            stroke-dasharray="4 4"
            vector-effect="non-scaling-stroke"
          />
        {/if}
        {#if item.area}
          <path d={item.area} fill={item.lane.color} fill-opacity="0.18" />
        {/if}
        {#if item.secondary}
          <path
            d={item.secondary}
            fill="none"
            stroke={item.lane.color}
            stroke-opacity="0.45"
            stroke-dasharray="3 3"
            stroke-width="1.2"
            vector-effect="non-scaling-stroke"
          />
        {/if}
        <path
          d={item.line}
          fill="none"
          stroke={item.lane.color}
          stroke-width="1.8"
          stroke-linejoin="round"
          vector-effect="non-scaling-stroke"
        />
        {#if hoverX !== null}
          <line
            x1={hoverX}
            x2={hoverX}
            y1="0"
            y2={HEIGHT}
            class="stroke-base-content/60"
            stroke-width="1"
            vector-effect="non-scaling-stroke"
          />
        {/if}
      </svg>
    </div>
  {/each}
  <div
    class="grid grid-cols-[7.5rem_1fr] gap-3 text-xs text-base-content/60 tabular-nums sm:grid-cols-[10rem_1fr]"
  >
    <span></span>
    <div class="flex justify-between">
      <span>0 km</span>
      <span>{hover === null ? "" : `km ${number((distances[hover] ?? 0) / 1000, 2)}`}</span>
      <span>{number(total / 1000, 2)} km</span>
    </div>
  </div>
</div>
