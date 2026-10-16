<script lang="ts">
  import { seriesVar } from "$lib/charts/theme";
  import type { SleepNight, SleepSeriesPoint } from "$lib/data/types";
  import { hours, number } from "$lib/format";
  import {
    clockLabel,
    hourTicks,
    nearestPoint,
    type LanePoint,
    type LaneReference,
  } from "$lib/lanes";
  import LaneChart from "./LaneChart.svelte";

  const { night }: { night: SleepNight } = $props();

  const LEFT = 44;
  const RIGHT = 8;
  const STAGE_HEIGHT = 112;
  const STAGES = ["awake", "rem", "light", "deep"] as const;
  type Stage = (typeof STAGES)[number];
  const STAGE_LABEL: Record<Stage, string> = {
    awake: "Acordado",
    rem: "REM",
    light: "Leve",
    deep: "Profundo",
  };
  const STAGE_SHORT: Record<Stage, string> = {
    awake: "acord.",
    rem: "REM",
    light: "leve",
    deep: "prof.",
  };
  const STAGE_COLOR: Record<Stage, string> = {
    awake: seriesVar(3),
    rem: seriesVar(2),
    light: seriesVar(4),
    deep: seriesVar(0),
  };

  let width = $state(600);
  let hover = $state<number | null>(null);

  const start = $derived(Math.min(...night.stages.map((stage) => stage.start_ms)));
  const end = $derived(Math.max(...night.stages.map((stage) => stage.end_ms)));
  const ticks = $derived(hourTicks(start, end));
  const x = (ts: number): number =>
    LEFT + ((ts - start) / Math.max(1, end - start)) * (width - LEFT - RIGHT);
  const band = (STAGE_HEIGHT - 8) / STAGES.length;
  const rowOf = (stage: string): number => Math.max(0, STAGES.indexOf(stage as Stage));

  const totals = $derived.by(() => {
    const sums: Record<Stage, number> = { awake: 0, rem: 0, light: 0, deep: 0 };
    for (const stage of night.stages) sums[stage.stage as Stage] += stage.end_ms - stage.start_ms;
    const all = Object.values(sums).reduce((sum, value) => sum + value, 0) || 1;
    return STAGES.map((stage) => ({
      stage,
      ms: sums[stage],
      pct: Math.round((sums[stage] / all) * 100),
    }));
  });
  const stageAt = (ts: number): Stage | null =>
    (night.stages.find((stage) => ts >= stage.start_ms && ts < stage.end_ms)?.stage as
      Stage | undefined) ?? null;

  const toPoints = (series: SleepSeriesPoint[]): LanePoint[] =>
    series.map((point) => ({ x: point.ts_ms, y: point.value }));
  const stressBands: LaneReference[] = [
    { y: 25, label: "descanso" },
    { y: 50, label: "baixo" },
    { y: 75, label: "médio" },
  ];
  const lanes = $derived(
    [
      {
        key: "hr",
        label: "FC",
        unit: "bpm",
        points: toPoints(night.hr),
        color: "var(--series-8)",
        yDomain: null,
        references: [],
      },
      {
        key: "hrv",
        label: "VFC",
        unit: "ms",
        points: toPoints(night.hrv),
        color: "var(--series-1)",
        yDomain: null,
        references: [],
      },
      {
        key: "body_battery",
        label: "Body Battery",
        unit: "0–100",
        points: toPoints(night.body_battery),
        color: "var(--series-3)",
        yDomain: [0, 100] as [number, number],
        references: [],
      },
      {
        key: "stress",
        label: "Estresse",
        unit: "0–100",
        points: toPoints(night.stress),
        color: "var(--series-4)",
        yDomain: [0, 100] as [number, number],
        references: stressBands,
      },
    ].filter((lane) => lane.points.length > 1),
  );
  const average = (points: LanePoint[]): number | null => {
    const values = points
      .map((point) => point.y)
      .filter((value): value is number => value !== null);
    return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  };

  const onMove = (event: PointerEvent): void => {
    const box = (event.currentTarget as SVGElement).getBoundingClientRect();
    const ratio = (event.clientX - box.left - LEFT) / Math.max(1, box.width - LEFT - RIGHT);
    hover = start + Math.min(1, Math.max(0, ratio)) * (end - start);
  };
  const hoverStage = $derived(hover === null ? null : stageAt(hover));
</script>

{#if night.stages.length}
  <div class="flex flex-col gap-2">
    <ul class="flex flex-wrap gap-x-5 gap-y-1 text-xs">
      {#each [...totals].reverse() as item (item.stage)}
        <li class="inline-flex items-center gap-1.5">
          <i class="size-2.5 rounded-sm" style:background={STAGE_COLOR[item.stage]}></i>
          <span>{STAGE_LABEL[item.stage]}</span>
          <span class="text-base-content/60 tabular-nums"
            >{hours(item.ms / 1000)} · {item.pct}%</span
          >
        </li>
      {/each}
    </ul>

    <div class="grid grid-cols-[7.5rem_1fr] items-start gap-2 sm:grid-cols-[10rem_1fr]">
      <div class="min-w-0 pt-1 text-xs">
        <p class="text-base-content/70">Fase</p>
        <p class="text-sm font-semibold">{hoverStage ? STAGE_LABEL[hoverStage] : "—"}</p>
        <p class="text-base-content/50 tabular-nums">
          {hover === null ? "passe o mouse" : clockLabel(hover)}
        </p>
      </div>
      <div bind:clientWidth={width} class="w-full">
        <svg
          {width}
          height={STAGE_HEIGHT}
          class="block touch-none select-none"
          role="img"
          aria-label="Fases do sono ao longo da noite"
          onpointermove={onMove}
          onpointerleave={() => (hover = null)}
        >
          {#each STAGES as stage, row (stage)}
            <rect
              x={LEFT}
              y={4 + row * band}
              width={Math.max(0, width - LEFT - RIGHT)}
              height={band}
              class={row % 2 ? "fill-base-content/[0.03]" : "fill-transparent"}
            />
            <text
              x={LEFT - 6}
              y={4 + row * band + band / 2}
              dy="0.32em"
              text-anchor="end"
              class="fill-base-content/60 text-[10px]">{STAGE_SHORT[stage]}</text
            >
          {/each}
          {#each ticks as tick (tick.value)}
            <line
              x1={x(tick.value)}
              x2={x(tick.value)}
              y1="4"
              y2={STAGE_HEIGHT - 4}
              class="stroke-base-content/10"
            />
          {/each}
          {#each night.stages as stage (stage.start_ms)}
            <rect
              x={x(stage.start_ms)}
              y={4 + rowOf(stage.stage) * band + 2}
              width={Math.max(1, x(stage.end_ms) - x(stage.start_ms))}
              height={band - 4}
              rx="2"
              style:fill={STAGE_COLOR[stage.stage as Stage]}
            />
          {/each}
          <line
            x1={x(start)}
            x2={x(start)}
            y1="4"
            y2={STAGE_HEIGHT - 4}
            class="stroke-base-content/50"
            stroke-dasharray="3 3"
          />
          <line
            x1={x(end)}
            x2={x(end)}
            y1="4"
            y2={STAGE_HEIGHT - 4}
            class="stroke-base-content/50"
            stroke-dasharray="3 3"
          />
          {#if hover !== null}
            <line
              x1={x(hover)}
              x2={x(hover)}
              y1="4"
              y2={STAGE_HEIGHT - 4}
              class="stroke-base-content/60"
            />
          {/if}
        </svg>
        <div
          class="flex justify-between text-[10px] text-base-content/60 tabular-nums"
          style:padding-left="{LEFT}px"
          style:padding-right="{RIGHT}px"
        >
          <span>dormiu {clockLabel(start)}</span>
          <span>acordou {clockLabel(end)}</span>
        </div>
      </div>
    </div>

    {#each lanes as lane, index (lane.key)}
      {@const hovered = hover === null ? null : nearestPoint(lane.points, hover)}
      {@const mean = average(lane.points)}
      <div class="grid grid-cols-[7.5rem_1fr] items-start gap-2 sm:grid-cols-[10rem_1fr]">
        <div class="min-w-0 pt-1 text-xs">
          <p class="text-base-content/70">
            {lane.label} <span class="text-base-content/45">({lane.unit})</span>
          </p>
          <p class="text-sm font-semibold tabular-nums">
            {#if hovered && hovered.y !== null}{number(
                hovered.y,
              )}{:else if hover === null && mean !== null}{number(mean)}{:else}—{/if}
          </p>
          <p class="text-base-content/50">
            {hover === null ? "média da noite" : clockLabel(hover)}
          </p>
        </div>
        <LaneChart
          points={lane.points}
          xDomain={[start, end]}
          xTicks={ticks}
          format={(value) => number(value)}
          color={lane.color}
          label="{lane.label} durante o sono"
          yDomain={lane.yDomain}
          references={lane.references}
          showXLabels={index === lanes.length - 1}
          bind:hover
        />
      </div>
    {/each}
  </div>
{:else}
  <p class="text-sm text-base-content/70">Sem fases registradas nesta noite.</p>
{/if}
