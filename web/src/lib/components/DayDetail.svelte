<script lang="ts">
  import type { DaySpan, Intraday, IntradayPoint } from "$lib/data/types";
  import { hours, number } from "$lib/format";
  import {
    clockLabel,
    hourTicks,
    nearestPoint,
    niceScale,
    type LanePoint,
    type LaneReference,
    type LaneSpan,
  } from "$lib/lanes";
  import LaneChart from "./LaneChart.svelte";

  const { day, partial }: { day: Intraday; partial: boolean } = $props();

  const SPAN_COLOR: Record<DaySpan["kind"], string> = {
    sleep: "var(--series-7)",
    activity: "var(--series-2)",
    motion: "var(--color-base-content)",
  };
  const SPAN_LABEL: Record<DaySpan["kind"], string> = {
    sleep: "sleep",
    activity: "activity",
    motion: "moving (no stress reading)",
  };
  const SHARE_COLOR: Record<string, string> = {
    rest: "var(--series-1)",
    low: "color-mix(in oklab, var(--series-4) 40%, var(--color-base-100))",
    medium: "color-mix(in oklab, var(--series-4) 70%, var(--color-base-100))",
    high: "var(--series-4)",
  };
  const STEP_BUCKET_MS = 15 * 60 * 1000;
  const stressReferences: LaneReference[] = [
    { y: 25, label: "rest" },
    { y: 50, label: "low" },
    { y: 75, label: "medium" },
  ];

  let hover = $state<number | null>(null);

  const ticks = $derived(hourTicks(day.start_ms, day.end_ms, 3));
  const toPoints = (series: IntradayPoint[]): LanePoint[] =>
    series.map((point) => ({ x: point.ts_ms, y: point.value }));
  const toSpans = (kinds: DaySpan["kind"][]): LaneSpan[] =>
    day.spans
      .filter((span) => kinds.includes(span.kind))
      .map((span) => ({
        from: span.start_ms,
        to: span.end_ms,
        color: SPAN_COLOR[span.kind],
        label: span.kind === "activity" ? span.label : undefined,
      }));
  const steps = $derived(
    day.steps.map((bucket) => ({ x: (bucket.start_ms + bucket.end_ms) / 2, y: bucket.steps })),
  );
  const stepsTop = $derived(
    niceScale(0, Math.max(100, ...steps.map((point) => point.y)), 3).domain[1],
  );
  const shareTotal = $derived(
    day.stress_shares.reduce((sum, share) => sum + share.minutes, 0) || 1,
  );
  const kindsPresent = $derived(
    (["sleep", "activity", "motion"] as const).filter((kind) =>
      day.spans.some((span) => span.kind === kind),
    ),
  );
  const activities = $derived(day.spans.filter((span) => span.kind === "activity"));
  const spanAt = (ts: number): DaySpan | null =>
    day.spans.find((span) => span.kind !== "motion" && ts >= span.start_ms && ts < span.end_ms) ??
    null;
  const hoverSpan = $derived(hover === null ? null : spanAt(hover));

  const lanes = $derived(
    [
      {
        key: "hr",
        label: "HR",
        unit: "bpm",
        points: toPoints(day.hr),
        color: "var(--series-8)",
        yDomain: null,
        references: [],
        spans: toSpans(["sleep", "activity"]),
        barWidth: null,
        summary:
          day.hr_min === null
            ? "—"
            : `${number(day.hr_min)}–${number(day.hr_max)}${day.hr_resting === null ? "" : ` · resting ${number(day.hr_resting)}`}`,
      },
      {
        key: "stress",
        label: "Stress",
        unit: "0–100",
        points: toPoints(day.stress),
        color: "var(--series-4)",
        yDomain: [0, 100] as [number, number],
        references: stressReferences,
        spans: toSpans(["sleep", "activity", "motion"]),
        barWidth: null,
        summary: day.stress_avg === null ? "—" : `avg ${number(day.stress_avg)}`,
      },
      {
        key: "body_battery",
        label: "Body Battery",
        unit: "0–100",
        points: toPoints(day.body_battery),
        color: "var(--series-3)",
        yDomain: [0, 100] as [number, number],
        references: [],
        spans: toSpans(["sleep", "activity"]),
        barWidth: null,
        summary:
          day.body_battery_high === null
            ? "—"
            : `${number(day.body_battery_low)}–${number(day.body_battery_high)}`,
      },
      {
        key: "steps",
        label: "Steps",
        unit: "per 15 min",
        points: steps,
        color: "var(--series-1)",
        yDomain: [0, stepsTop] as [number, number],
        references: [],
        spans: toSpans(["sleep", "activity"]),
        barWidth: STEP_BUCKET_MS,
        summary: day.steps_total === null ? "—" : `${number(day.steps_total)} for the day`,
      },
    ].filter((lane) => lane.points.some((point) => point.y !== null)),
  );
</script>

<section class="card border border-base-content/10 bg-base-100" aria-labelledby="day-detail">
  <div class="card-body gap-3 p-5">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 id="day-detail" class="text-base font-semibold">The day in detail</h2>
      {#if partial && day.last_sample_ms !== null}
        <p class="text-xs text-warning">
          data up to {clockLabel(day.last_sample_ms)}: sync again to see the rest of the day
        </p>
      {/if}
    </div>
    <p class="text-xs text-base-content/70">
      Midnight to midnight. Stress is only measured at rest: the watch does not calculate it while
      you move.
    </p>

    {#if day.stress_shares.length}
      <div class="flex flex-col gap-1.5">
        <div
          class="flex h-3 w-full overflow-hidden rounded-sm"
          role="img"
          aria-label="Time at each stress level"
        >
          {#each day.stress_shares as share (share.key)}
            <span
              style:width="{(share.minutes / shareTotal) * 100}%"
              style:background={SHARE_COLOR[share.key]}
              class="h-full border-r-2 border-base-100 last:border-r-0"
            ></span>
          {/each}
        </div>
        <ul class="flex flex-wrap gap-x-5 gap-y-1 text-xs">
          {#each day.stress_shares as share (share.key)}
            <li class="inline-flex items-center gap-1.5">
              <i class="size-2.5 rounded-sm" style:background={SHARE_COLOR[share.key]}></i>
              <span>{share.label} stress</span>
              <span class="text-base-content/60 tabular-nums">{hours(share.minutes * 60)}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if kindsPresent.length}
      <ul class="flex flex-wrap gap-x-5 gap-y-1 text-xs text-base-content/70">
        {#each kindsPresent as kind (kind)}
          <li class="inline-flex items-center gap-1.5">
            <i
              class="h-3 w-4 rounded-sm"
              style:background="color-mix(in oklab, {SPAN_COLOR[kind]} 22%, transparent)"
            ></i>
            {SPAN_LABEL[kind]}
          </li>
        {/each}
        {#each activities as activity (activity.start_ms)}
          <li class="tabular-nums">
            {activity.label}
            {clockLabel(activity.start_ms)}–{clockLabel(activity.end_ms)}
          </li>
        {/each}
      </ul>
    {/if}

    <div class="flex flex-col gap-1">
      {#each lanes as lane, index (lane.key)}
        {@const hovered = hover === null ? null : nearestPoint(lane.points, hover)}
        <div class="grid grid-cols-[7.5rem_1fr] items-start gap-2 sm:grid-cols-[10rem_1fr]">
          <div class="min-w-0 pt-1 text-xs">
            <p class="truncate text-base-content/70">
              {lane.label} <span class="text-base-content/45">({lane.unit})</span>
            </p>
            <p class="text-sm font-semibold tabular-nums">
              {#if hover === null}{lane.summary}{:else if hovered && hovered.y !== null}{number(
                  hovered.y,
                )}{:else}—{/if}
            </p>
            {#if index === 0}
              <p class="truncate text-base-content/50 tabular-nums">
                {hover === null
                  ? "hover to inspect"
                  : `${clockLabel(hover)}${hoverSpan ? ` · ${hoverSpan.label}` : ""}`}
              </p>
            {/if}
          </div>
          <LaneChart
            points={lane.points}
            xDomain={[day.start_ms, day.end_ms]}
            xTicks={ticks}
            format={(value) => number(value)}
            color={lane.color}
            label="{lane.label} over the day"
            yDomain={lane.yDomain}
            references={lane.references}
            spans={lane.spans}
            barWidth={lane.barWidth}
            area={lane.key === "body_battery"}
            showXLabels={index === lanes.length - 1}
            bind:hover
          />
        </div>
      {/each}
    </div>
  </div>
</section>
