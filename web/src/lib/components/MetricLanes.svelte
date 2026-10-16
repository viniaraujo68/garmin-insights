<script lang="ts">
  import type { Streams, ZoneTime } from "$lib/data/types";
  import { delta, number, pace } from "$lib/format";
  import {
    kmTicks,
    nearestPoint,
    pauses,
    type LaneBand,
    type LanePoint,
    type LaneReference,
  } from "$lib/lanes";
  import { nearestByDistance, smooth } from "$lib/streams";
  import LaneChart from "./LaneChart.svelte";

  let {
    streams,
    zones = [],
    hover = $bindable(null),
  }: { streams: Streams; zones?: ZoneTime[]; hover?: number | null } = $props();

  interface Lane {
    key: string;
    label: string;
    unit: string;
    values: (number | null)[];
    secondary?: (number | null)[];
    secondaryLabel?: string;
    format: (value: number) => string;
    tickFormat?: (value: number) => string;
    reverse?: boolean;
    area?: boolean;
    references?: LaneReference[];
    bands?: LaneBand[];
    color: string;
  }

  const distances = $derived(streams.distance_m);
  const totalKm = $derived(
    Math.max(0.1, ...distances.filter((value): value is number => value !== null)) / 1000,
  );
  const breaks = $derived(pauses(streams.elapsed_s, distances));
  const breakIndexes = $derived(new Set(breaks.map((item) => item.index)));
  const ticks = $derived(kmTicks(totalKm));

  const toPoints = (values: (number | null)[]): LanePoint[] => {
    const points: LanePoint[] = [];
    values.forEach((value, index) => {
      const distance = distances[index];
      if (distance === null || distance === undefined) return;
      if (breakIndexes.has(index)) points.push({ x: distance / 1000 - 1e-6, y: null });
      points.push({ x: distance / 1000, y: value });
    });
    return points;
  };

  const zoneBands = $derived<LaneBand[]>(
    zones
      .filter((zone) => zone.floor_bpm !== null)
      .map((zone) => ({
        from: zone.floor_bpm ?? 0,
        to: zone.ceiling_bpm ?? (zone.floor_bpm ?? 0) + 20,
        color: `color-mix(in oklab, var(--ramp-hr-high) ${(zone.zone - 1) * 25}%, var(--ramp-hr-low))`,
        label: `Z${zone.zone}`,
      })),
  );
  const lanes = $derived<Lane[]>(
    [
      {
        key: "pace",
        label: "Pace",
        unit: "min/km",
        values: smooth(streams.pace_s_km, 6),
        secondary: smooth(streams.gap_pace_s_km, 6),
        secondaryLabel: "ajustado à inclinação",
        format: (value: number) => `${pace(value)}/km`,
        tickFormat: (value: number) => pace(value),
        reverse: true,
        color: "var(--series-1)",
      },
      {
        key: "hr",
        label: "FC",
        unit: "bpm",
        values: smooth(streams.hr, 2),
        format: (value: number) => `${number(value)} bpm`,
        tickFormat: (value: number) => number(value),
        color: "var(--series-8)",
        bands: zoneBands,
      },
      {
        key: "cadence",
        label: "Cadência",
        unit: "ppm",
        values: smooth(streams.cadence, 4),
        format: (value: number) => `${number(value)} ppm`,
        tickFormat: (value: number) => number(value),
        color: "var(--series-7)",
      },
      {
        key: "power",
        label: "Potência",
        unit: "W",
        values: smooth(streams.power, 4),
        format: (value: number) => `${number(value)} W`,
        tickFormat: (value: number) => number(value),
        color: "var(--series-4)",
      },
      {
        key: "elevation",
        label: "Altitude",
        unit: "m",
        values: streams.elevation,
        format: (value: number) => `${number(value)} m`,
        tickFormat: (value: number) => number(value),
        area: true,
        color: "var(--series-3)",
      },
      {
        key: "condition",
        label: "Condição de desempenho",
        unit: "",
        values: streams.performance_condition,
        format: (value: number) => delta(value),
        references: [{ y: 0, label: "seu normal" }],
        color: "var(--series-2)",
      },
    ].filter((lane) => lane.values.some((value) => value !== null)),
  );

  const drawn = $derived(
    lanes.map((lane) => {
      const points = toPoints(lane.values);
      const present = lane.values.filter((value): value is number => value !== null);
      return {
        lane,
        points,
        secondary: lane.secondary ? toPoints(lane.secondary) : [],
        mean: present.length
          ? present.reduce((sum, value) => sum + value, 0) / present.length
          : null,
        firstKm: points.find((point) => point.y !== null)?.x ?? null,
      };
    }),
  );

  const hoverKm = $derived(hover === null ? null : (distances[hover] ?? 0) / 1000);
  const setHoverKm = (value: number | null): void => {
    hover = value === null ? null : nearestByDistance(distances, value * 1000);
  };
  const conditionLate = $derived.by(() => {
    const condition = drawn.find((item) => item.lane.key === "condition");
    return condition?.firstKm !== null &&
      condition?.firstKm !== undefined &&
      condition.firstKm > 1.5
      ? condition.firstKm
      : null;
  });
</script>

<div class="flex flex-col gap-1">
  {#each drawn as item, index (item.lane.key)}
    {@const hovered = hoverKm === null ? null : nearestPoint(item.points, hoverKm)}
    {@const hoveredSecondary =
      hoverKm === null || !item.secondary.length ? null : nearestPoint(item.secondary, hoverKm)}
    <div class="grid grid-cols-[7.5rem_1fr] items-start gap-2 sm:grid-cols-[10rem_1fr]">
      <div class="min-w-0 pt-1 text-xs">
        <p class="truncate text-base-content/70">
          {item.lane.label}
          {#if item.lane.unit}<span class="text-base-content/45">({item.lane.unit})</span>{/if}
        </p>
        <p class="text-sm font-semibold tabular-nums">
          {#if hovered && hovered.y !== null}{item.lane.format(
              hovered.y,
            )}{:else if hoverKm === null && item.mean !== null}{item.lane.format(
              item.mean,
            )}{:else}—{/if}
        </p>
        {#if hoverKm === null}
          <p class="text-base-content/50">média</p>
        {:else if hoveredSecondary && hoveredSecondary.y !== null}
          <p class="truncate text-base-content/60 tabular-nums">
            {item.lane.format(hoveredSecondary.y)}
            {item.lane.secondaryLabel}
          </p>
        {/if}
        {#if item.lane.key === "condition" && conditionLate !== null}
          <p class="text-warning">medida a partir de {number(conditionLate, 1)} km</p>
        {/if}
      </div>
      <LaneChart
        points={item.points}
        secondary={item.secondary}
        xDomain={[0, totalKm]}
        xTicks={ticks}
        format={item.lane.format}
        tickFormat={item.lane.tickFormat}
        color={item.lane.color}
        label="{item.lane.label} ao longo da corrida"
        reverse={item.lane.reverse}
        area={item.lane.area}
        references={item.lane.references}
        bands={item.lane.bands}
        markers={index === 0
          ? breaks.map((entry) => entry.marker)
          : breaks.map((entry) => ({ x: entry.marker.x, label: "" }))}
        showXLabels={index === drawn.length - 1}
        bind:hover={() => hoverKm, setHoverKm}
      />
    </div>
  {/each}
  <p class="pl-[7.5rem] text-xs text-base-content/60 sm:pl-[10rem]">
    {hoverKm === null
      ? "Passe o mouse para ver o valor de cada faixa no mesmo ponto."
      : `km ${number(hoverKm, 2)}`}
  </p>
</div>
