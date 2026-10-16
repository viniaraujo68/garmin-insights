<script lang="ts">
  import type { SleepNight, SleepSeriesPoint } from "$lib/data/types";
  import { number } from "$lib/format";

  const { night }: { night: SleepNight } = $props();

  const WIDTH = 1000;
  const STAGE_HEIGHT = 120;
  const LANE_HEIGHT = 56;
  const STAGES = ["awake", "rem", "light", "deep"] as const;
  const STAGE_LABEL: Record<string, string> = {
    awake: "Acordado",
    rem: "REM",
    light: "Leve",
    deep: "Profundo",
  };
  const STAGE_COLOR: Record<string, string> = {
    awake: "var(--series-4)",
    rem: "var(--series-3)",
    light: "var(--ramp-low)",
    deep: "var(--ramp-high)",
  };

  const start = $derived(
    Math.min(
      ...night.stages.map((stage) => stage.start_ms),
      ...night.hr.map((point) => point.ts_ms),
    ),
  );
  const end = $derived(
    Math.max(...night.stages.map((stage) => stage.end_ms), ...night.hr.map((point) => point.ts_ms)),
  );
  const x = (ts: number): number => ((ts - start) / Math.max(1, end - start)) * WIDTH;
  const band = STAGE_HEIGHT / STAGES.length;
  const rowOf = (stage: string): number =>
    Math.max(0, STAGES.indexOf(stage as (typeof STAGES)[number]));

  const lanes = $derived(
    [
      { key: "hr", label: "FC", unit: "bpm", points: night.hr, color: "var(--series-8)" },
      { key: "hrv", label: "VFC", unit: "ms", points: night.hrv, color: "var(--series-1)" },
      {
        key: "body_battery",
        label: "Body Battery",
        unit: "",
        points: night.body_battery,
        color: "var(--series-3)",
      },
      {
        key: "stress",
        label: "Estresse",
        unit: "",
        points: night.stress,
        color: "var(--series-4)",
      },
    ].filter((lane) => lane.points.length > 1),
  );

  const path = (points: SleepSeriesPoint[]): string => {
    const values = points.map((point) => point.value);
    const low = Math.min(...values);
    const high = Math.max(...values);
    const scale = (value: number): number =>
      LANE_HEIGHT - 4 - ((value - low) / Math.max(1, high - low)) * (LANE_HEIGHT - 8);
    return points
      .map(
        (point, index) =>
          `${index ? "L" : "M"}${x(point.ts_ms).toFixed(1)},${scale(point.value).toFixed(1)}`,
      )
      .join("");
  };
  const average = (points: SleepSeriesPoint[]): number =>
    points.reduce((sum, point) => sum + point.value, 0) / points.length;
  const clock = (ts: number): string =>
    new Intl.DateTimeFormat("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "America/Sao_Paulo",
    }).format(new Date(ts));
  const hourTicks = $derived.by(() => {
    const ticks: number[] = [];
    const first = Math.ceil(start / 3_600_000) * 3_600_000;
    for (let ts = first; ts <= end; ts += 3_600_000) ticks.push(ts);
    return ticks;
  });
</script>

{#if night.stages.length}
  <div class="flex flex-col gap-2">
    <div class="grid grid-cols-[6rem_1fr] gap-3">
      <div
        class="flex flex-col justify-around text-xs text-base-content/70"
        style:height="{STAGE_HEIGHT}px"
      >
        {#each STAGES as stage (stage)}<span class="inline-flex items-center gap-1.5"
            ><i class="size-2.5 rounded-full" style:background={STAGE_COLOR[stage]}
            ></i>{STAGE_LABEL[stage]}</span
          >{/each}
      </div>
      <svg
        viewBox="0 0 {WIDTH} {STAGE_HEIGHT}"
        preserveAspectRatio="none"
        class="w-full"
        style:height="{STAGE_HEIGHT}px"
        role="img"
        aria-label="Fases do sono ao longo da noite"
      >
        {#each STAGES as _, row (row)}
          <rect
            x="0"
            y={row * band}
            width={WIDTH}
            height={band}
            class={row % 2 ? "fill-base-content/[0.03]" : "fill-transparent"}
          />
        {/each}
        {#each night.stages as stage (stage.start_ms)}
          <rect
            x={x(stage.start_ms)}
            y={rowOf(stage.stage) * band + 3}
            width={Math.max(1, x(stage.end_ms) - x(stage.start_ms))}
            height={band - 6}
            rx="2"
            style:fill={STAGE_COLOR[stage.stage]}
          >
            <title>{STAGE_LABEL[stage.stage]} · {clock(stage.start_ms)}–{clock(stage.end_ms)}</title
            >
          </rect>
        {/each}
      </svg>
    </div>
    {#each lanes as lane (lane.key)}
      <div class="grid grid-cols-[6rem_1fr] items-center gap-3">
        <div class="text-xs">
          <p class="text-base-content/70">{lane.label}</p>
          <p class="font-semibold tabular-nums">média {number(average(lane.points))} {lane.unit}</p>
        </div>
        <svg
          viewBox="0 0 {WIDTH} {LANE_HEIGHT}"
          preserveAspectRatio="none"
          class="h-14 w-full"
          role="img"
          aria-label="{lane.label} durante o sono"
        >
          <rect width={WIDTH} height={LANE_HEIGHT} class="fill-base-content/[0.03]" />
          <path
            d={path(lane.points)}
            fill="none"
            stroke={lane.color}
            stroke-width="1.6"
            vector-effect="non-scaling-stroke"
          />
        </svg>
      </div>
    {/each}
    <div class="grid grid-cols-[6rem_1fr] gap-3 text-xs text-base-content/60 tabular-nums">
      <span></span>
      <div class="relative h-4">
        {#each hourTicks as tick (tick)}
          <span class="absolute -translate-x-1/2" style:left="{(x(tick) / WIDTH) * 100}%"
            >{clock(tick)}</span
          >
        {/each}
      </div>
    </div>
  </div>
{:else}
  <p class="text-sm text-base-content/70">Sem fases registradas nesta noite.</p>
{/if}
