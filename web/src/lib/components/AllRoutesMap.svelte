<script lang="ts" module>
  export type RoutesMode = "frequency" | "pace" | "hr";
</script>

<script lang="ts">
  import "leaflet/dist/leaflet.css";
  import type { LayerGroup, Map as LeafletMap } from "leaflet";
  import { onMount } from "svelte";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { readChartColors } from "$lib/charts/theme";
  import { interpolate, robustRange } from "$lib/color";
  import type { Routes } from "$lib/data/types";
  import { pace } from "$lib/format";

  const { routes, mode }: { routes: Routes; mode: RoutesMode } = $props();

  const TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

  const theme = getThemeContext();
  let container = $state<HTMLDivElement>();
  let leaflet = $state<typeof import("leaflet")>();
  let map = $state<LeafletMap>();
  let layer: LayerGroup | undefined;
  let fitted = false;
  let legend = $state<{ from: string; to: string; stops: string[] } | null>(null);

  onMount(() => {
    let disposed = false;
    let created: LeafletMap | undefined;
    void import("leaflet").then((module) => {
      if (disposed || !container) return;
      const L = (module as unknown as { default?: typeof module }).default ?? module;
      created = L.map(container, { renderer: L.canvas({ padding: 0.5 }), scrollWheelZoom: false });
      L.tileLayer(TILE_URL, { attribution: ATTRIBUTION, maxZoom: 19 }).addTo(created);
      leaflet = L;
      map = created;
    });
    return () => {
      disposed = true;
      created?.remove();
    };
  });

  $effect(() => {
    const L = leaflet;
    const target = map;
    const host = container;
    const chosen = mode;
    void theme.dark;
    if (!L || !target || !host) return;
    layer?.remove();
    const colors = readChartColors(host);
    const group = L.layerGroup().addTo(target);
    const metric = chosen === "hr" ? 3 : 2;
    const values = routes.routes.flatMap((route) =>
      route.points.map((point) => point[metric] ?? null),
    );
    const [low, high] = robustRange(values);
    const ramp =
      chosen === "hr"
        ? interpolate(colors.hrLow, colors.hrHigh)
        : interpolate(colors.rampLow, colors.rampHigh);
    const colorOf = (value: number | null): string => {
      if (value === null || high === low) return colors.neutral;
      const t = (value - low) / (high - low);
      return ramp(chosen === "pace" ? 1 - t : t);
    };
    const bounds: [number, number][] = [];
    for (const route of routes.routes) {
      const points = route.points.filter((point) => point[0] !== null && point[1] !== null) as [
        number,
        number,
        number | null,
        number | null,
      ][];
      bounds.push(...points.map((point) => [point[0], point[1]] as [number, number]));
      if (chosen === "frequency") {
        L.polyline(
          points.map((point) => [point[0], point[1]]),
          { color: colors.series[0] ?? colors.ink, weight: 4, opacity: 0.28, interactive: false },
        ).addTo(group);
        continue;
      }
      for (let index = 1; index < points.length; index += 1) {
        const from = points[index - 1]!;
        const to = points[index]!;
        L.polyline(
          [
            [from[0], from[1]],
            [to[0], to[1]],
          ],
          { color: colorOf(to[metric] ?? null), weight: 4, opacity: 0.8, interactive: false },
        ).addTo(group);
      }
    }
    if (!fitted && bounds.length) {
      target.fitBounds(L.latLngBounds(bounds), { padding: [20, 20] });
      fitted = true;
    }
    legend =
      chosen === "frequency"
        ? null
        : {
            from: chosen === "pace" ? `${pace(high)}/km (lento)` : `${Math.round(low)} bpm`,
            to: chosen === "pace" ? `${pace(low)}/km (rápido)` : `${Math.round(high)} bpm`,
            stops: Array.from({ length: 6 }, (_, index) => ramp(index / 5)),
          };
    layer = group;
    return () => group.remove();
  });
</script>

<div
  class={[
    "map-wrap relative isolate overflow-hidden rounded-box border border-base-content/10",
    theme.dark && "map-dark",
  ]}
>
  <div bind:this={container} class="h-[clamp(360px,65vh,720px)] w-full"></div>
</div>
{#if legend}
  <div class="mt-2 flex items-center gap-3 text-xs text-base-content/70 tabular-nums">
    <span>{legend.from}</span>
    <i
      class="h-2 min-w-24 flex-1 rounded-full"
      style:background="linear-gradient(90deg, {legend.stops.join(', ')})"
    ></i>
    <span>{legend.to}</span>
  </div>
{:else}
  <p class="mt-2 text-xs text-base-content/70">
    Onde as linhas se acumulam e escurecem é onde você mais corre.
  </p>
{/if}

<style>
  .map-wrap :global(.leaflet-tile-pane) {
    filter: grayscale(1) contrast(0.9) brightness(1.04);
    opacity: 0.85;
  }
  .map-dark :global(.leaflet-tile-pane) {
    filter: grayscale(1) invert(1) brightness(0.8) contrast(0.85);
    opacity: 0.9;
  }
  .map-wrap :global(.leaflet-container) {
    background: var(--color-base-200);
    font: inherit;
  }
</style>
