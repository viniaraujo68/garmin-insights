<script lang="ts">
  import type { IllnessWatch } from "$lib/data/types";
  import { delta, number } from "$lib/format";

  const { watch }: { watch: IllnessWatch } = $props();

  const TONE: Record<string, string> = {
    ok: "border-success/40",
    watch: "border-warning/50",
    alert: "border-error/60",
    insufficient: "border-base-content/10",
  };
  const TITLE: Record<string, string> = {
    ok: "Everything in your normal range",
    watch: "One signal outside your normal",
    alert: "Attention: signs of fatigue or illness",
    insufficient: "Still learning your normal",
  };
</script>

<section class={["card border bg-base-100", TONE[watch.status]]} aria-labelledby="illness">
  <div class="card-body gap-3 p-5">
    <div class="flex flex-col gap-1">
      <h2 id="illness" class="text-base font-semibold">{TITLE[watch.status]}</h2>
      <p class="text-sm text-base-content/70">{watch.message}</p>
    </div>
    <ul class="grid gap-2 sm:grid-cols-3">
      {#each watch.signals as signal (signal.key)}
        <li
          class={[
            "rounded-box border p-3",
            signal.flagged ? "border-error/50 bg-error/5" : "border-base-content/10",
          ]}
        >
          <p class="text-xs text-base-content/70">{signal.label}</p>
          <p class="text-lg font-semibold tabular-nums">
            {number(signal.value)}
            <span class="text-xs font-normal text-base-content/60">{signal.unit}</span>
          </p>
          <p class="text-xs text-base-content/60 tabular-nums">
            your normal {number(signal.median, 1)} · {signal.z === null
              ? "no deviation"
              : `${delta(signal.z, 1)} SD`}
          </p>
        </li>
      {/each}
    </ul>
    <p class="text-xs text-base-content/50">
      Compares tonight's reading with the median of the nights between 30 and 3 days ago ({watch.reference_nights}
      nights). One signal alone is common; two together deserve attention. Not a diagnosis.
    </p>
  </div>
</section>
