<script lang="ts">
  import type { RouteTrace } from "$lib/data/types";
  import { robustRange } from "$lib/color";

  const { route }: { route: RouteTrace } = $props();

  const WIDTH = 160;
  const HEIGHT = 120;
  const MARGIN = 10;

  const segments = $derived.by(() => {
    const points = route.points.filter(([lat, lon]) => lat !== null && lon !== null) as [
      number,
      number,
      number | null,
    ][];
    if (points.length < 2) return [];
    const latitude =
      (points.reduce((sum, point) => sum + point[0], 0) / points.length) * (Math.PI / 180);
    const projected = points.map(([lat, lon]) => [lon * Math.cos(latitude), -lat] as const);
    const xs = projected.map(([x]) => x);
    const ys = projected.map(([, y]) => y);
    const spanX = Math.max(...xs) - Math.min(...xs);
    const spanY = Math.max(...ys) - Math.min(...ys);
    const scale = Math.min(
      (WIDTH - MARGIN * 2) / (spanX || 1e-9),
      (HEIGHT - MARGIN * 2) / (spanY || 1e-9),
    );
    const offsetX = WIDTH / 2 - ((Math.max(...xs) + Math.min(...xs)) / 2) * scale;
    const offsetY = HEIGHT / 2 - ((Math.max(...ys) + Math.min(...ys)) / 2) * scale;
    const [fast, slow] = robustRange(points.map((point) => point[2]));
    const mix = (pace: number | null): number =>
      pace === null || slow === fast ? 50 : Math.round(((slow - pace) / (slow - fast)) * 100);
    return projected.slice(1).flatMap(([x, y], index) => {
      const previous = projected[index];
      const point = points[index + 1];
      if (!previous || !point) return [];
      const pct = Math.min(100, Math.max(0, mix(point[2])));
      return [
        {
          x1: previous[0] * scale + offsetX,
          y1: previous[1] * scale + offsetY,
          x2: x * scale + offsetX,
          y2: y * scale + offsetY,
          color: `color-mix(in oklab, var(--ramp-high) ${pct}%, var(--ramp-low))`,
        },
      ];
    });
  });
</script>

<svg
  viewBox="0 0 {WIDTH} {HEIGHT}"
  class="aspect-[4/3] w-full"
  role="img"
  aria-label="Percurso da corrida de {route.date}"
>
  {#each segments as segment, index (index)}
    <line
      x1={segment.x1}
      y1={segment.y1}
      x2={segment.x2}
      y2={segment.y2}
      stroke={segment.color}
      style:stroke={segment.color}
      stroke-width="2.6"
      stroke-linecap="round"
    />
  {/each}
</svg>
