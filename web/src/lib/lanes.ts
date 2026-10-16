export interface LanePoint {
  x: number;
  y: number | null;
}

export interface LaneTick {
  value: number;
  label: string;
}

export interface LaneMarker {
  x: number;
  label: string;
}

export interface LaneReference {
  y: number;
  label: string;
}

export interface LaneBand {
  from: number;
  to: number;
  color: string;
  label?: string;
}

const PAUSE_SECONDS = 30;
const hourFormat = new Intl.DateTimeFormat("pt-BR", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "America/Sao_Paulo",
});

export const nearestPoint = (points: LanePoint[], x: number): LanePoint | null => {
  if (!points.length) return null;
  let low = 0;
  let high = points.length - 1;
  while (high - low > 1) {
    const middle = Math.floor((low + high) / 2);
    if (points[middle].x < x) low = middle;
    else high = middle;
  }
  const a = points[low];
  const b = points[high];
  return Math.abs(a.x - x) <= Math.abs(b.x - x) ? a : b;
};

export const clockLabel = (timestampMs: number): string => hourFormat.format(new Date(timestampMs));

export const hourTicks = (startMs: number, endMs: number): LaneTick[] => {
  const ticks: LaneTick[] = [];
  const first = Math.ceil(startMs / 3_600_000) * 3_600_000;
  for (let value = first; value <= endMs; value += 3_600_000)
    ticks.push({ value, label: clockLabel(value) });
  return ticks;
};

const kmStep = (totalKm: number): number => {
  if (totalKm > 25) return 5;
  if (totalKm > 12) return 2;
  return 1;
};

export const kmTicks = (totalKm: number): LaneTick[] => {
  const size = kmStep(totalKm);
  const ticks: LaneTick[] = [];
  for (let value = 0; value <= totalKm + 1e-9; value += size)
    ticks.push({ value, label: `${value} km` });
  return ticks;
};

export const pauses = (
  elapsed: (number | null)[],
  distance: (number | null)[],
): { index: number; marker: LaneMarker }[] => {
  const found: { index: number; marker: LaneMarker }[] = [];
  for (let index = 1; index < elapsed.length; index += 1) {
    const before = elapsed[index - 1];
    const after = elapsed[index];
    const where = distance[index];
    if (before === null || after === null || where === null) continue;
    const gap = after - before;
    if (gap >= PAUSE_SECONDS)
      found.push({
        index,
        marker: { x: where / 1000, label: `pausa ${Math.round(gap / 60)} min` },
      });
  }
  return found;
};

export const niceScale = (
  low: number,
  high: number,
  targetTicks = 3,
): { domain: [number, number]; ticks: number[] } => {
  const span = high - low || Math.abs(high) || 1;
  const rough = span / targetTicks;
  const magnitude = 10 ** Math.floor(Math.log10(rough));
  const step =
    [1, 2, 2.5, 5, 10]
      .map((factor) => factor * magnitude)
      .find((candidate) => candidate >= rough) ?? 10 * magnitude;
  const start = Math.floor(low / step) * step;
  const end = Math.ceil(high / step) * step;
  const ticks: number[] = [];
  for (let value = start; value <= end + step / 1e6; value += step)
    ticks.push(Math.round(value * 1e6) / 1e6);
  return { domain: [start, end], ticks };
};
