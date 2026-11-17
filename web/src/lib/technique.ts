export interface TechniqueBand {
  key:
    "cadence" | "stride_m" | "ground_contact_ms" | "vertical_oscillation_cm" | "vertical_ratio_pct";
  label: string;
  unit: string;
  digits: 0 | 1 | 2;
  higherIsBetter: boolean;
  limits: [number, number, number, number] | null;
  help: string;
}

export const TECHNIQUE: TechniqueBand[] = [
  {
    key: "cadence",
    label: "Cadence",
    unit: "spm",
    digits: 0,
    higherIsBetter: true,
    limits: [153, 164, 174, 184],
    help: "Steps per minute. Average: 164–173.",
  },
  {
    key: "stride_m",
    label: "Stride",
    unit: "m",
    digits: 2,
    higherIsBetter: true,
    limits: null,
    help: "Depends on height and speed: no range.",
  },
  {
    key: "ground_contact_ms",
    label: "Ground contact time",
    unit: "ms",
    digits: 0,
    higherIsBetter: false,
    limits: [218, 249, 278, 309],
    help: "Lower is better. Average: 249–277 ms.",
  },
  {
    key: "vertical_oscillation_cm",
    label: "Vertical oscillation",
    unit: "cm",
    digits: 1,
    higherIsBetter: false,
    limits: [6.4, 8.2, 9.8, 11.6],
    help: "Lower is better. Average: 8.2–9.7 cm.",
  },
  {
    key: "vertical_ratio_pct",
    label: "Vertical ratio",
    unit: "%",
    digits: 1,
    higherIsBetter: false,
    limits: [6.1, 7.5, 8.7, 10.2],
    help: "Lower is better. Average: 7.5–8.6%.",
  },
];

const RANKS = [
  { status: "good", label: "elite" },
  { status: "good", label: "good" },
  { status: "typical", label: "average" },
  { status: "attention", label: "below average" },
  { status: "bad", label: "low" },
] as const;

export const techniqueRank = (
  band: TechniqueBand,
  value: number | null,
): { status: string; label: string } => {
  if (value === null || band.limits === null) return { status: "unknown", label: "no range" };
  const below = band.limits.filter((limit) => value >= limit).length;
  const index = band.higherIsBetter ? 4 - below : below;
  return RANKS[index] ?? { status: "unknown", label: "—" };
};
