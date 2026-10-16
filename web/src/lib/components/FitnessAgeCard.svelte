<script lang="ts">
  import type { FitnessAge } from "$lib/data/types";
  import { number } from "$lib/format";

  const { age }: { age: FitnessAge } = $props();

  const progress = (value: number | null, target: number | null): number =>
    value === null || !target ? 0 : Math.min(100, (value / target) * 100);
</script>

<article class="card border border-base-content/10 bg-base-100">
  <div class="card-body gap-3 p-5">
    <h2 class="text-base font-semibold">Idade fitness</h2>
    <div class="flex items-baseline gap-3">
      <span class="text-5xl font-semibold tracking-tight tabular-nums"
        >{number(age.fitness_age)}</span
      >
      <span class="text-sm text-base-content/70"
        >anos · idade real {number(age.chronological_age)}</span
      >
    </div>
    <p class="text-sm text-base-content/70">
      A idade de quem tem o seu condicionamento, pelo VO2max, FC de repouso e atividade vigorosa.
    </p>
    {#each [{ label: "Dias vigorosos por semana", value: age.vigorous_days_per_week, target: age.vigorous_days_target, digits: 1 }, { label: "Minutos vigorosos por semana", value: age.vigorous_minutes_per_week, target: age.vigorous_minutes_target, digits: 0 }] as item (item.label)}
      <div class="flex flex-col gap-1 text-xs">
        <div class="flex justify-between">
          <span>{item.label}</span>
          <span class="tabular-nums"
            ><b>{number(item.value, item.digits as 0 | 1)}</b> de {number(item.target)}</span
          >
        </div>
        <progress
          class="progress w-full progress-primary"
          value={progress(item.value, item.target)}
          max="100"
        ></progress>
      </div>
    {/each}
  </div>
</article>
