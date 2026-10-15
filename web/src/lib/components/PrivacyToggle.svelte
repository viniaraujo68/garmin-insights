<script lang="ts">
  import { privacySetting } from "$lib/privacy.svelte";

  const { radius }: { radius: number | null } = $props();
  const id = $props.id();
</script>

{#if radius !== null}
  <label class="label cursor-pointer gap-2 text-sm" for={id}>
    <input
      {id}
      type="checkbox"
      class="toggle toggle-sm"
      checked={privacySetting.hideHome}
      onchange={(event) => privacySetting.toggle(event.currentTarget.checked)}
    />
    Esconder {radius} m em volta de casa (para print)
  </label>
{/if}
