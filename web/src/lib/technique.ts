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
    label: "Cadência",
    unit: "ppm",
    digits: 0,
    higherIsBetter: true,
    limits: [153, 164, 174, 184],
    help: "Passos por minuto. Média: 164–173.",
  },
  {
    key: "stride_m",
    label: "Passada",
    unit: "m",
    digits: 2,
    higherIsBetter: true,
    limits: null,
    help: "Depende da altura e da velocidade: sem faixa.",
  },
  {
    key: "ground_contact_ms",
    label: "Contato com o solo",
    unit: "ms",
    digits: 0,
    higherIsBetter: false,
    limits: [218, 249, 278, 309],
    help: "Menos é melhor. Média: 249–277 ms.",
  },
  {
    key: "vertical_oscillation_cm",
    label: "Oscilação vertical",
    unit: "cm",
    digits: 1,
    higherIsBetter: false,
    limits: [6.4, 8.2, 9.8, 11.6],
    help: "Menos é melhor. Média: 8,2–9,7 cm.",
  },
  {
    key: "vertical_ratio_pct",
    label: "Razão vertical",
    unit: "%",
    digits: 1,
    higherIsBetter: false,
    limits: [6.1, 7.5, 8.7, 10.2],
    help: "Menos é melhor. Média: 7,5–8,6%.",
  },
];

const RANKS = [
  { status: "good", label: "elite" },
  { status: "good", label: "bom" },
  { status: "typical", label: "na média" },
  { status: "attention", label: "abaixo da média" },
  { status: "bad", label: "baixo" },
] as const;

export const techniqueRank = (
  band: TechniqueBand,
  value: number | null,
): { status: string; label: string } => {
  if (value === null || band.limits === null) return { status: "unknown", label: "sem faixa" };
  const below = band.limits.filter((limit) => value >= limit).length;
  const index = band.higherIsBetter ? 4 - below : below;
  return RANKS[index] ?? { status: "unknown", label: "—" };
};
