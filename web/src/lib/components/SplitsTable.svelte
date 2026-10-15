<script lang="ts">
  import { DataTable, type Column } from "@viniaraujo68/plinth/table";
  import type { Lap } from "$lib/data/types";
  import { number, pace } from "$lib/format";

  const { laps }: { laps: Lap[] } = $props();

  const full = $derived(
    laps.filter((lap) => (lap.distance_m ?? 0) >= 950 && lap.pace_s_km !== null),
  );
  const fastest = $derived(Math.min(...full.map((lap) => lap.pace_s_km ?? Infinity)));
  const slowest = $derived(Math.max(...full.map((lap) => lap.pace_s_km ?? 0)));
  const width = (lap: Lap): number => {
    if (lap.pace_s_km === null || (lap.distance_m ?? 0) < 950) return 8;
    if (slowest === fastest) return 100;
    return 20 + ((slowest - lap.pace_s_km) / (slowest - fastest)) * 80;
  };

  const columns: Column<Lap>[] = $derived([
    {
      key: "lap",
      label: "Km",
      numeric: true,
      hideable: false,
      value: (lap) =>
        lap.distance_m !== null && lap.distance_m < 950
          ? `${number(lap.distance_m)} m`
          : String(lap.lap),
      sortBy: (lap) => lap.lap,
    },
    {
      key: "pace_s_km",
      label: "Pace",
      cell: paceCell,
      sortBy: (lap) => lap.pace_s_km,
      defaultSortDirection: "asc",
      minWidth: 160,
    },
    {
      key: "gap_pace_s_km",
      label: "Pace ajustado",
      numeric: true,
      value: (lap) => pace(lap.gap_pace_s_km),
      sortBy: (lap) => lap.gap_pace_s_km,
    },
    {
      key: "avg_hr",
      label: "FC",
      numeric: true,
      value: (lap) => number(lap.avg_hr),
      sortBy: (lap) => lap.avg_hr,
    },
    {
      key: "cadence",
      label: "Cadência",
      numeric: true,
      value: (lap) => number(lap.cadence),
      sortBy: (lap) => lap.cadence,
    },
    {
      key: "stride_m",
      label: "Passada",
      numeric: true,
      value: (lap) => number(lap.stride_m, 2),
      sortBy: (lap) => lap.stride_m,
    },
    {
      key: "ground_contact_ms",
      label: "Contato",
      numeric: true,
      value: (lap) => number(lap.ground_contact_ms),
      sortBy: (lap) => lap.ground_contact_ms,
      hiddenByDefault: true,
    },
    {
      key: "power_w",
      label: "Potência",
      numeric: true,
      value: (lap) => number(lap.power_w),
      sortBy: (lap) => lap.power_w,
      hiddenByDefault: true,
    },
    {
      key: "elevation_gain_m",
      label: "Subida",
      numeric: true,
      value: (lap) => `${number(lap.elevation_gain_m)} m`,
      sortBy: (lap) => lap.elevation_gain_m,
    },
  ]);
</script>

{#snippet paceCell(lap: Lap)}
  <span class="flex items-center gap-2">
    <span class="h-2 w-24 shrink-0 overflow-hidden rounded-field bg-base-content/5">
      <span
        class={[
          "block h-full rounded-[inherit]",
          lap.pace_s_km === fastest ? "bg-[var(--series-1)]" : "bg-base-content/30",
        ]}
        style:width="{width(lap)}%"
      ></span>
    </span>
    <span class={["tabular-nums", lap.pace_s_km === fastest && "font-semibold"]}
      >{pace(lap.pace_s_km)}</span
    >
  </span>
{/snippet}

<DataTable
  rows={laps}
  {columns}
  rowKey={(lap) => lap.lap}
  label="Splits por km"
  storageKey="passada:splits"
  sortLabel={(column) => `Ordenar por ${column.label}`}
/>
