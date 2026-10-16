<script lang="ts">
  import "leaflet/dist/leaflet.css";
  import type { CircleMarker, LayerGroup, LeafletMouseEvent, Map as LeafletMap } from "leaflet";
  import { onMount } from "svelte";
  import { getThemeContext } from "@viniaraujo68/plinth/theme";
  import { readChartColors } from "$lib/charts/theme";
  import type { Streams, ZoneTime } from "$lib/data/types";
  import { pace } from "$lib/format";
  import { colorScale, type ColorBy, type ColorScale } from "$lib/streams";

  let {
    streams,
    zones,
    colorBy,
    hover = $bindable(null),
  }: {
    streams: Streams;
    zones: ZoneTime[];
    colorBy: ColorBy;
    hover?: number | null;
  } = $props();

  const TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  const HOVER_PIXELS = 28;

  const theme = getThemeContext();
  let container = $state<HTMLDivElement>();
  let leaflet = $state<typeof import("leaflet")>();
  let map = $state<LeafletMap>();
  let routeLayer: LayerGroup | undefined;
  let hoverMarker: CircleMarker | undefined;
  let scale = $state<ColorScale>();
  let visible: number[] = [];
  let fittedFor: Streams | undefined;

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
    const by = colorBy;
    void theme.dark;
    if (!L || !target || !host) return;

    routeLayer?.remove();
    const colors = readChartColors(host);
    const current = colorScale(streams, by, zones, colors);
    scale = current;
    visible = streams.lat
      .map((_lat, index) => index)
      .filter((index) => {
        const lat = streams.lat[index];
        const lon = streams.lon[index];
        return lat !== null && lat !== undefined && lon !== null && lon !== undefined;
      });
    const layer = L.layerGroup().addTo(target);
    const point = (index: number): [number, number] => [
      streams.lat[index] ?? 0,
      streams.lon[index] ?? 0,
    ];
    const outline = colors.surface;
    let run: [number, number][] = [];
    let previous: number | null = null;
    for (const index of visible) {
      if (previous !== null && index - previous > 1) {
        if (run.length > 1)
          L.polyline(run, { color: outline, weight: 8, opacity: 0.9, interactive: false }).addTo(
            layer,
          );
        run = [];
      }
      run.push(point(index));
      previous = index;
    }
    if (run.length > 1)
      L.polyline(run, { color: outline, weight: 8, opacity: 0.9, interactive: false }).addTo(layer);
    for (let position = 1; position < visible.length; position += 1) {
      const from = visible[position - 1]!;
      const to = visible[position]!;
      if (to - from > 1) continue;
      L.polyline([point(from), point(to)], {
        color: current.color(to),
        weight: 5,
        opacity: 1,
        lineCap: "round",
        interactive: false,
      }).addTo(layer);
    }
    let nextKm = 1000;
    for (const index of visible) {
      const traveled = streams.distance_m[index];
      if (traveled === null || traveled === undefined || traveled < nextKm) continue;
      L.marker(point(index), {
        interactive: false,
        icon: L.divIcon({
          className: "passada-km",
          html: String(Math.round(nextKm / 1000)),
          iconSize: [22, 22],
        }),
      }).addTo(layer);
      nextKm += 1000;
    }
    const first = visible[0];
    const last = visible[visible.length - 1];
    if (first !== undefined && last !== undefined) {
      L.circleMarker(point(first), {
        radius: 7,
        color: outline,
        weight: 2,
        fillColor: "#16a34a",
        fillOpacity: 1,
        interactive: false,
      }).addTo(layer);
      L.circleMarker(point(last), {
        radius: 7,
        color: outline,
        weight: 2,
        fillColor: "#dc2626",
        fillOpacity: 1,
        interactive: false,
      }).addTo(layer);
    }
    hoverMarker = L.circleMarker([0, 0], {
      radius: 8,
      color: outline,
      weight: 3,
      fillColor: colors.ink,
      fillOpacity: 1,
      interactive: false,
    });
    if (visible.length && fittedFor !== streams) {
      target.fitBounds(L.latLngBounds(visible.map(point)), { padding: [24, 24] });
      fittedFor = streams;
    }
    routeLayer = layer;

    const onMove = (event: LeafletMouseEvent): void => {
      let best: number | null = null;
      let bestDistance = Infinity;
      for (const index of visible) {
        const distance = target
          .latLngToContainerPoint(point(index))
          .distanceTo(event.containerPoint);
        if (distance < bestDistance) {
          bestDistance = distance;
          best = index;
        }
      }
      hover = bestDistance <= HOVER_PIXELS ? best : null;
    };
    const onOut = (): void => {
      hover = null;
    };
    target.on("mousemove", onMove);
    target.on("mouseout", onOut);
    return () => {
      target.off("mousemove", onMove);
      target.off("mouseout", onOut);
      layer.remove();
    };
  });

  $effect(() => {
    const target = map;
    const marker = hoverMarker;
    const index = hover;
    if (!target || !marker || !routeLayer) return;
    const lat = index === null ? null : streams.lat[index];
    const lon = index === null ? null : streams.lon[index];
    if (
      index === null ||
      lat === null ||
      lat === undefined ||
      lon === null ||
      lon === undefined ||
      !visible.includes(index)
    ) {
      marker.remove();
      return;
    }
    marker.setLatLng([lat, lon]).addTo(routeLayer);
  });

  const hoverLabel = $derived.by(() => {
    if (hover === null) return null;
    const distance = streams.distance_m[hover];
    return {
      km:
        distance === null || distance === undefined
          ? "—"
          : (distance / 1000).toFixed(2).replace(".", ","),
      pace: pace(streams.pace_s_km[hover]),
      hr: streams.hr[hover] ?? null,
    };
  });
</script>

<div
  class={[
    "map-wrap relative isolate overflow-hidden rounded-box border border-base-content/10",
    theme.dark && "map-dark",
  ]}
>
  <div bind:this={container} class="h-[clamp(320px,55vh,560px)] w-full"></div>
  {#if hoverLabel}
    <div
      class="pointer-events-none absolute top-3 right-3 z-[1000] rounded-field border border-base-content/10 bg-base-100/95 px-3 py-2 text-xs tabular-nums shadow"
    >
      <b>km {hoverLabel.km}</b> · {hoverLabel.pace}/km · {hoverLabel.hr ?? "—"} bpm
    </div>
  {/if}
</div>
{#if scale}
  <div class="mt-2 flex flex-wrap items-center gap-3 text-xs text-base-content/70 tabular-nums">
    {#if scale.legend.kind === "gradient"}
      <span>{scale.legend.from}</span>
      <i
        class="h-2 min-w-24 flex-1 rounded-full"
        style:background="linear-gradient(90deg, {scale.legend.stops.join(', ')})"
      ></i>
      <span>{scale.legend.to}</span>
    {:else}
      {#each scale.legend.items as item (item.label)}
        <span class="inline-flex items-center gap-1.5"
          ><i class="size-2.5 rounded-full" style:background={item.color}></i>{item.label}</span
        >
      {/each}
    {/if}
  </div>
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
  .map-wrap :global(.passada-km) {
    display: grid;
    place-items: center;
    border-radius: 9999px;
    background: var(--color-base-100);
    color: var(--color-base-content);
    border: 1.5px solid var(--color-base-content);
    font-size: 11px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
</style>
