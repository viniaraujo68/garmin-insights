<script lang="ts">
  import { SegmentedControl } from "@viniaraujo68/plinth/components";
  import AllRoutesMap, { type RoutesMode } from "$lib/components/AllRoutesMap.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import { number } from "$lib/format";

  const { data } = $props();
  let mode = $state<RoutesMode>("frequency");

  const total = $derived(
    data.routes.routes.reduce((sum, route) => sum + (route.distance_km ?? 0), 0),
  );
</script>

<PageFrame
  title="Mapas"
  description="Todas as suas corridas sobrepostas: onde você mais corre, em que trechos vai mais rápido e onde a FC sobe."
>
  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="todas">
    <div class="card-body gap-3 p-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 id="todas" class="text-base font-semibold">
            {data.routes.routes.length} corridas · {number(total, 1)} km
          </h2>
          <p class="text-xs text-base-content/70">
            Use os botões para trocar o que a cor mostra. A escala de pace e FC é a mesma para todas
            as corridas.
          </p>
        </div>
        <SegmentedControl
          options={[
            { id: "frequency", label: "Frequência" },
            { id: "pace", label: "Pace" },
            { id: "hr", label: "FC" },
          ]}
          bind:value={mode}
          label="Colorir por"
          caption="Colorir por"
          size="sm"
        />
      </div>
      <AllRoutesMap routes={data.routes} {mode} />
    </div>
  </section>
</PageFrame>
