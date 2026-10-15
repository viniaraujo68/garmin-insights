<script lang="ts">
  const {
    values,
    bandLow = null,
    bandHigh = null,
    label,
  }: {
    values: (number | null)[];
    bandLow?: number | null;
    bandHigh?: number | null;
    label: string;
  } = $props();

  const WIDTH = 120;
  const HEIGHT = 32;
  const PAD = 3;

  const present = $derived(values.filter((value): value is number => value !== null));
  const extent = $derived.by(() => {
    const all = [
      ...present,
      ...(bandLow === null ? [] : [bandLow]),
      ...(bandHigh === null ? [] : [bandHigh]),
    ];
    const low = Math.min(...all);
    const high = Math.max(...all);
    return high === low ? [low - 1, high + 1] : [low, high];
  });
  const x = (index: number): number =>
    PAD + (index / Math.max(1, values.length - 1)) * (WIDTH - PAD * 2);
  const y = (value: number): number =>
    HEIGHT -
    PAD -
    ((value - (extent[0] ?? 0)) / ((extent[1] ?? 1) - (extent[0] ?? 0))) * (HEIGHT - PAD * 2);
  const path = $derived(
    values
      .map((value, index) =>
        value === null ? null : `${x(index).toFixed(1)},${y(value).toFixed(1)}`,
      )
      .reduce<string[]>((parts, point, index, all) => {
        if (point === null) return parts;
        parts.push(`${index === 0 || all[index - 1] === null ? "M" : "L"}${point}`);
        return parts;
      }, [])
      .join(" "),
  );
</script>

{#if present.length >= 2}
  <svg
    class="h-8 w-full"
    viewBox="0 0 {WIDTH} {HEIGHT}"
    preserveAspectRatio="none"
    role="img"
    aria-label={label}
  >
    {#if bandLow !== null && bandHigh !== null}
      <rect
        x={PAD}
        width={WIDTH - PAD * 2}
        y={y(bandHigh)}
        height={Math.max(1, y(bandLow) - y(bandHigh))}
        class="fill-success/15"
      />
    {/if}
    <path
      d={path}
      fill="none"
      stroke="var(--series-1)"
      stroke-width="1.6"
      stroke-linejoin="round"
      stroke-linecap="round"
      vector-effect="non-scaling-stroke"
    />
  </svg>
{:else}
  <div class="h-8"></div>
{/if}
