import type { ChartColors } from "$lib/charts/theme";
import type { Streams, ZoneTime } from "$lib/data/types";
import { interpolate, robustRange } from "$lib/color";

export type ColorBy = "pace" | "hr" | "zone" | "grade";

export const COLOR_BY_OPTIONS: { id: ColorBy; label: string }[] = [
  { id: "pace", label: "Pace" },
  { id: "hr", label: "FC" },
  { id: "zone", label: "Zona de FC" },
  { id: "grade", label: "Inclinação" },
];

const GRADE_LIMIT = 8;

export const smooth = (values: (number | null)[], radius: number): (number | null)[] =>
  values.map((value, index) => {
    if (value === null) return null;
    let sum = 0;
    let count = 0;
    const first = Math.max(0, index - radius);
    const last = Math.min(values.length - 1, index + radius);
    for (let position = first; position <= last; position += 1) {
      const item = values[position];
      if (item !== null) {
        sum += item;
        count += 1;
      }
    }
    return count ? sum / count : null;
  });

export const nearestByDistance = (distances: (number | null)[], target: number): number | null => {
  let best: number | null = null;
  let bestGap = Infinity;
  distances.forEach((distance, index) => {
    if (distance === null) return;
    const gap = Math.abs(distance - target);
    if (gap < bestGap) {
      bestGap = gap;
      best = index;
    }
  });
  return best;
};

export const zoneOf = (hr: number | null, zones: ZoneTime[]): number | null => {
  if (hr === null) return null;
  let current: number | null = null;
  for (const zone of zones)
    if (zone.floor_bpm !== null && hr >= zone.floor_bpm) current = zone.zone;
  return current ?? (zones.length ? 1 : null);
};

export interface ColorScale {
  color: (index: number) => string;
  legend:
    | { kind: "gradient"; from: string; to: string; stops: string[] }
    | { kind: "swatches"; items: { label: string; color: string }[] };
}

export const colorScale = (
  streams: Streams,
  by: ColorBy,
  zones: ZoneTime[],
  colors: ChartColors,
): ColorScale => {
  const neutral = colors.neutral;
  if (by === "pace") {
    const pace = smooth(streams.pace_s_km, 5);
    const [fast, slow] = robustRange(pace);
    const ramp = interpolate(colors.rampLow, colors.rampHigh);
    return {
      color: (index) => {
        const value = pace[index];
        return value === null || slow === fast ? neutral : ramp((slow - value) / (slow - fast));
      },
      legend: {
        kind: "gradient",
        from: `${formatPace(slow)} (lento)`,
        to: `${formatPace(fast)} (rápido)`,
        stops: steps(ramp),
      },
    };
  }
  if (by === "hr") {
    const hr = smooth(streams.hr, 3);
    const [low, high] = robustRange(hr);
    const ramp = interpolate(colors.hrLow, colors.hrHigh);
    return {
      color: (index) => {
        const value = hr[index];
        return value === null || high === low ? neutral : ramp((value - low) / (high - low));
      },
      legend: {
        kind: "gradient",
        from: `${Math.round(low)} bpm`,
        to: `${Math.round(high)} bpm`,
        stops: steps(ramp),
      },
    };
  }
  if (by === "zone") {
    const ramp = interpolate(colors.hrLow, colors.hrHigh);
    const zoneColor = (zone: number): string => ramp((zone - 1) / 4);
    return {
      color: (index) => {
        const zone = zoneOf(streams.hr[index] ?? null, zones);
        return zone === null ? neutral : zoneColor(zone);
      },
      legend: {
        kind: "swatches",
        items: zones.map((zone) => ({
          label: `Z${zone.zone} ${zone.floor_bpm ?? ""}${zone.ceiling_bpm ? `–${zone.ceiling_bpm - 1}` : "+"}`,
          color: zoneColor(zone.zone),
        })),
      },
    };
  }
  const grade = smooth(streams.grade_pct, 3);
  const down = interpolate(neutral, colors.series[2] ?? neutral);
  const up = interpolate(neutral, colors.series[1] ?? neutral);
  return {
    color: (index) => {
      const value = grade[index];
      if (value === null) return neutral;
      const strength = Math.min(1, Math.abs(value) / GRADE_LIMIT);
      return value >= 0 ? up(strength) : down(strength);
    },
    legend: {
      kind: "gradient",
      from: `descida ${GRADE_LIMIT}%`,
      to: `subida ${GRADE_LIMIT}%`,
      stops: [...steps(down).reverse(), ...steps(up)],
    },
  };
};

const steps = (ramp: (t: number) => string): string[] =>
  Array.from({ length: 6 }, (_, index) => ramp(index / 5));

const formatPace = (seconds: number): string => {
  const total = Math.round(seconds);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
};
