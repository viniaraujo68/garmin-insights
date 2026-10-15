<script lang="ts">
  const { status, label }: { status: string; label: string } = $props();

  const TONE: Record<string, string> = {
    good: "text-success",
    typical: "text-base-content/70",
    attention: "text-warning",
    bad: "text-error",
    unknown: "text-base-content/50",
  };
  const ICON: Record<string, string> = {
    good: "M5 12.5l4 4 10-10",
    typical: "M5 12h14",
    attention: "M12 7v6M12 17h.01",
    bad: "M7 7l10 10M17 7 7 17",
    unknown: "M12 17h.01M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.7",
  };
</script>

<span
  class={["inline-flex items-center gap-1 text-xs font-medium", TONE[status] ?? TONE["unknown"]]}
>
  <svg
    class="size-3.5 shrink-0"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2.4"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path d={ICON[status] ?? ICON["unknown"]} />
  </svg>
  {label}
</span>
