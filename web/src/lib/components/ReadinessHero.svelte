<script lang="ts">
  import type { Readiness } from "$lib/data/types";
  import { date } from "$lib/format";
  import { labelOf, READINESS_FEEDBACK, READINESS_LEVEL } from "$lib/labels";

  const {
    readiness,
    trainingStatus,
  }: { readiness: Readiness | null; trainingStatus: string | null } = $props();

  const tone = (score: number): string => {
    if (score >= 75) return "text-success";
    if (score >= 50) return "text-base-content";
    if (score >= 25) return "text-warning";
    return "text-error";
  };
  const factorTone = (pct: number): string => {
    if (pct >= 75) return "badge-success";
    if (pct >= 50) return "badge-neutral";
    if (pct >= 30) return "badge-warning";
    return "badge-error";
  };
</script>

<section class="card border border-base-content/10 bg-base-100" aria-labelledby="prontidao">
  <div class="card-body gap-4 p-5 sm:flex-row sm:items-center sm:gap-8">
    {#if readiness}
      <div class="flex shrink-0 flex-col">
        <h2 id="prontidao" class="text-xs font-medium tracking-wide text-base-content/70 uppercase">
          Prontidão para treinar
        </h2>
        <div class="flex items-baseline gap-2">
          <span
            class={["text-6xl font-semibold tracking-tight tabular-nums", tone(readiness.score)]}
            >{readiness.score}</span
          >
          <span class="text-lg text-base-content/70"
            >{labelOf(READINESS_LEVEL, readiness.level)}</span
          >
        </div>
        <p class="text-sm">{labelOf(READINESS_FEEDBACK, readiness.feedback)}</p>
        <p class="text-xs text-base-content/60">
          leitura da manhã de {date(readiness.date)}
          {#if readiness.recovery_time_h}· recuperação restante {readiness.recovery_time_h} h{/if}
          {#if trainingStatus}· status de treino: {trainingStatus}{/if}
        </p>
      </div>
      <div class="flex min-w-0 flex-1 flex-col gap-2">
        <p class="text-xs text-base-content/70">O que pesou, do pior para o melhor (% do ideal):</p>
        <ul class="flex flex-wrap gap-2">
          {#each readiness.factors as factor (factor.key)}
            <li class={["badge gap-1 badge-soft", factorTone(factor.pct)]}>
              {factor.label}<span class="font-semibold tabular-nums">{factor.pct}%</span>
            </li>
          {/each}
        </ul>
      </div>
    {:else}
      <p id="prontidao" class="text-sm text-base-content/70">
        Sem leitura de prontidão hoje. Ela aparece depois que o relógio sincroniza pela manhã.
      </p>
    {/if}
  </div>
</section>
