<script lang="ts">
  import type { FocusRow } from "$lib/data/types";
  import { number } from "$lib/format";
  import StatusText from "./StatusText.svelte";

  const { rows }: { rows: FocusRow[] } = $props();

  const scale = $derived(
    Math.max(1, ...rows.map((row) => Math.max(row.load ?? 0, row.target_max ?? 0))) * 1.05,
  );
  const pct = (value: number | null): number => ((value ?? 0) / scale) * 100;
  const statusLabel = (row: FocusRow): string => {
    if (row.status === "good") return "dentro do alvo";
    return (row.load ?? 0) < (row.target_min ?? 0) ? "abaixo do alvo" : "acima do alvo";
  };
  const HELP: Record<string, string> = {
    aerobic_low: "corridas leves, zonas 1–2",
    aerobic_high: "ritmo forte sustentado, zonas 3–4",
    anaerobic: "tiros curtos e intensos, zona 5",
  };
</script>

<ul class="flex flex-col gap-4">
  {#each rows as row (row.focus)}
    <li class="flex flex-col gap-1">
      <div class="flex flex-wrap items-baseline justify-between gap-2 text-sm">
        <span
          ><b>{row.label}</b>
          <span class="text-xs text-base-content/60">{HELP[row.focus] ?? ""}</span></span
        >
        <span class="tabular-nums"
          >{number(row.load)}
          <span class="text-xs text-base-content/60"
            >alvo {number(row.target_min)}–{number(row.target_max)}</span
          ></span
        >
      </div>
      <div class="relative h-4 w-full overflow-hidden rounded-field bg-base-content/5">
        <span
          class="absolute inset-y-0 border-x border-success/50 bg-success/20"
          style:left="{pct(row.target_min)}%"
          style:width="{pct(row.target_max) - pct(row.target_min)}%"
        ></span>
        <span
          class={[
            "absolute inset-y-1 left-0 rounded-field",
            row.status === "good" ? "bg-[var(--series-1)]" : "bg-warning",
          ]}
          style:width="{Math.max(0.6, pct(row.load))}%"
        ></span>
      </div>
      <StatusText status={row.status} label={statusLabel(row)} />
    </li>
  {/each}
</ul>
