<script lang="ts">
  const { positions }: { positions: number[][] } = $props();

  const WIDTH = 240;
  const HEIGHT = 160;
  const MARGIN = 8;

  const dots = $derived.by(() => {
    const points = positions.filter((point) => point.length >= 2) as [number, number][];
    if (points.length < 2) return [];
    const latitude =
      (points.reduce((sum, point) => sum + point[0], 0) / points.length) * (Math.PI / 180);
    const projected = points.map(([lat, lon]) => [lon * Math.cos(latitude), -lat] as const);
    const xs = projected.map(([x]) => x);
    const ys = projected.map(([, y]) => y);
    const scale = Math.min(
      (WIDTH - MARGIN * 2) / (Math.max(...xs) - Math.min(...xs) || 1e-9),
      (HEIGHT - MARGIN * 2) / (Math.max(...ys) - Math.min(...ys) || 1e-9),
    );
    const offsetX = WIDTH / 2 - ((Math.max(...xs) + Math.min(...xs)) / 2) * scale;
    const offsetY = HEIGHT / 2 - ((Math.max(...ys) + Math.min(...ys)) / 2) * scale;
    return projected.map(([x, y]) => ({ x: x * scale + offsetX, y: y * scale + offsetY }));
  });
</script>

{#if dots.length}
  <svg
    viewBox="0 0 {WIDTH} {HEIGHT}"
    class="w-full rounded-box bg-success/10"
    role="img"
    aria-label="Onde você esteve no campo"
  >
    {#each dots as dot, index (index)}
      <circle cx={dot.x} cy={dot.y} r="7" fill="var(--series-8)" fill-opacity="0.08" />
    {/each}
  </svg>
{:else}
  <p class="text-xs text-base-content/60">Sem GPS nesta sessão.</p>
{/if}
