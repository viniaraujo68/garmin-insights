type Rgb = [number, number, number];

const parse = (color: string): Rgb => {
  const hex = /^#([0-9a-f]{6})$/i.exec(color.trim());
  if (hex?.[1]) {
    const value = parseInt(hex[1], 16);
    return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
  }
  const numbers = color.match(/[\d.]+/g)?.map(Number) ?? [];
  return [numbers[0] ?? 0, numbers[1] ?? 0, numbers[2] ?? 0];
};

export const interpolate = (from: string, to: string): ((t: number) => string) => {
  const a = parse(from);
  const b = parse(to);
  return (t) => {
    const clamped = Math.min(1, Math.max(0, t));
    const channel = (index: 0 | 1 | 2): number =>
      Math.round(a[index] + (b[index] - a[index]) * clamped);
    return `rgb(${channel(0)}, ${channel(1)}, ${channel(2)})`;
  };
};

export const quantile = (sorted: number[], q: number): number => {
  if (sorted.length === 0) return 0;
  const position = (sorted.length - 1) * q;
  const low = Math.floor(position);
  const high = Math.ceil(position);
  const lowValue = sorted[low] ?? 0;
  const highValue = sorted[high] ?? lowValue;
  return lowValue + (highValue - lowValue) * (position - low);
};

export const robustRange = (values: (number | null | undefined)[]): [number, number] => {
  const sorted = values
    .filter(
      (value): value is number => value !== null && value !== undefined && Number.isFinite(value),
    )
    .sort((a, b) => a - b);
  return [quantile(sorted, 0.05), quantile(sorted, 0.95)];
};
