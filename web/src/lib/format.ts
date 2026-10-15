import { createFormatters } from "@viniaraujo68/plinth/formatters";

export const DASH = "—";

type Maybe = number | null | undefined;

const isMissing = (value: Maybe): value is null | undefined =>
  value === null || value === undefined || !Number.isFinite(value);

const fixed = (digits: number) =>
  new Intl.NumberFormat("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });

const FIXED = [fixed(0), fixed(1), fixed(2)] as const;

const signed = (digits: number) =>
  new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: "exceptZero",
  });

const SIGNED = [signed(0), signed(1), signed(2)] as const;

const dates = createFormatters("pt-BR", {
  date: { dateStyle: "short", timeZone: "UTC" },
  datetime: { dateStyle: "short", timeStyle: "short", timeZone: "America/Sao_Paulo" },
});

const shortDate = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  timeZone: "UTC",
});
const weekday = new Intl.DateTimeFormat("pt-BR", { weekday: "short", timeZone: "UTC" });
const longDay = new Intl.DateTimeFormat("pt-BR", {
  weekday: "long",
  day: "numeric",
  month: "long",
  timeZone: "UTC",
});

const pad2 = (value: number): string => String(value).padStart(2, "0");

export const number = (value: Maybe, digits: 0 | 1 | 2 = 0): string =>
  isMissing(value) ? DASH : FIXED[digits].format(value);

export const delta = (value: Maybe, digits: 0 | 1 | 2 = 0): string =>
  isMissing(value) ? DASH : SIGNED[digits].format(value).replace("-", "−");

export const pace = (secondsPerKm: Maybe): string => {
  if (isMissing(secondsPerKm)) return DASH;
  const total = Math.round(secondsPerKm);
  return `${Math.floor(total / 60)}:${pad2(total % 60)}`;
};

export const duration = (seconds: Maybe): string => {
  if (isMissing(seconds)) return DASH;
  const total = Math.round(seconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return hours ? `${hours}h${pad2(minutes)}` : `${minutes} min`;
};

export const clock = (seconds: Maybe): string => {
  if (isMissing(seconds)) return DASH;
  const total = Math.round(seconds);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  return hours ? `${hours}:${pad2(minutes)}:${pad2(total % 60)}` : `${minutes}:${pad2(total % 60)}`;
};

export const hours = (seconds: Maybe): string =>
  isMissing(seconds)
    ? DASH
    : `${Math.floor(seconds / 3600)}h${pad2(Math.round((seconds % 3600) / 60))}`;

export const km = (value: Maybe, digits: 0 | 1 | 2 = 1): string =>
  isMissing(value) ? DASH : `${FIXED[digits].format(value)} km`;

export const date = (value: string | null | undefined): string =>
  value ? dates.date(`${value.slice(0, 10)}T00:00:00Z`) : DASH;

export const dayMonth = (value: string): string =>
  shortDate.format(new Date(`${value.slice(0, 10)}T00:00:00Z`));

export const weekdayShort = (value: string): string =>
  weekday.format(new Date(`${value.slice(0, 10)}T00:00:00Z`)).replace(".", "");

export const dayTitle = (value: string): string => {
  const text = longDay.format(new Date(`${value.slice(0, 10)}T00:00:00Z`));
  return text.charAt(0).toUpperCase() + text.slice(1);
};

export const datetime = (value: string | null | undefined): string =>
  value ? dates.datetime(value) : DASH;
