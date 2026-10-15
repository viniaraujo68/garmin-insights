import { createCssColorReader } from "@viniaraujo68/plinth/theme";

export const SERIES_COUNT = 8;

export interface ChartColors {
  series: string[];
  seriesSoft: string[];
  ink: string;
  muted: string;
  grid: string;
  surface: string;
  rampLow: string;
  rampHigh: string;
  hrLow: string;
  hrHigh: string;
  critical: string;
  neutral: string;
}

const FALLBACK_SERIES = [
  "#2a78d6",
  "#eb6834",
  "#1baf7a",
  "#eda100",
  "#e87ba4",
  "#008300",
  "#6250d6",
  "#e34948",
];

export const readChartColors = (host: HTMLElement): ChartColors => {
  const reader = createCssColorReader(host);
  try {
    const read = (expression: string, fallback: string): string =>
      reader.read(expression, fallback);
    return {
      series: FALLBACK_SERIES.map((fallback, slot) => read(`var(--series-${slot + 1})`, fallback)),
      seriesSoft: FALLBACK_SERIES.map((fallback, slot) =>
        read(`color-mix(in srgb, var(--series-${slot + 1}) 22%, transparent)`, fallback),
      ),
      ink: read("var(--color-base-content)", "#1b1d22"),
      muted: read("color-mix(in srgb, var(--color-base-content) 65%, transparent)", "#6b6b6b"),
      grid: read("color-mix(in srgb, var(--color-base-content) 10%, transparent)", "#e5e5e5"),
      surface: read("var(--color-base-100)", "#ffffff"),
      rampLow: read("var(--ramp-low)", "#9ec5f4"),
      rampHigh: read("var(--ramp-high)", "#0d366b"),
      hrLow: read("var(--ramp-hr-low)", "#f7c7b1"),
      hrHigh: read("var(--ramp-hr-high)", "#8a2a07"),
      critical: read("var(--color-error)", "#d03b3b"),
      neutral: read("color-mix(in srgb, var(--color-base-content) 35%, transparent)", "#999999"),
    };
  } finally {
    reader.dispose();
  }
};

export const seriesColor = (colors: ChartColors, slot: number): string =>
  colors.series[slot % SERIES_COUNT] ?? colors.ink;

export const seriesVar = (slot: number): string => `var(--series-${(slot % SERIES_COUNT) + 1})`;
