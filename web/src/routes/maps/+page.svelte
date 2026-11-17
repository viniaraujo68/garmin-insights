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
  title="Maps"
  description="All your runs overlaid: where you run most, which stretches are fastest and where your HR climbs."
>
  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="all">
    <div class="card-body gap-3 p-5">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 id="all" class="text-base font-semibold">
            {data.routes.routes.length} runs · {number(total, 1)} km
          </h2>
          <p class="text-xs text-base-content/70">
            Use the buttons to change what the colour shows. The pace and HR scale is the same for
            all runs.
          </p>
        </div>
        <SegmentedControl
          options={[
            { id: "frequency", label: "Frequency" },
            { id: "pace", label: "Pace" },
            { id: "hr", label: "HR" },
          ]}
          bind:value={mode}
          label="Colour by"
          caption="Colour by"
          size="sm"
        />
      </div>
      <AllRoutesMap routes={data.routes} {mode} />
    </div>
  </section>
</PageFrame>
