<script lang="ts">
  import type { Signal } from "$lib/data/types";
  import StatusText from "./StatusText.svelte";

  const { signal }: { signal: Signal } = $props();

  const STATUS_LABEL: Record<string, string> = {
    good: "ok",
    typical: "normal",
    attention: "atenção",
    bad: "risco",
    unknown: "sem dado",
  };
</script>

<div class="flex flex-col gap-0.5">
  <span class="text-xs text-base-content/70">{signal.label}</span>
  <span class="text-xl font-semibold tabular-nums">{signal.display}</span>
  <StatusText status={signal.status} label={STATUS_LABEL[signal.status] ?? signal.status} />
  <span class="text-xs text-base-content/60">{signal.detail}</span>
</div>
