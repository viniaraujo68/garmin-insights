<script lang="ts">
  import type { Snippet } from "svelte";
  import { Breadcrumbs } from "@viniaraujo68/plinth/shell";

  const {
    title,
    description,
    header,
    children,
    breadcrumbs = false,
  }: {
    title: string;
    description?: string;
    header?: Snippet;
    children: Snippet;
    breadcrumbs?: boolean;
  } = $props();
</script>

<svelte:head>
  <title>{title} · garmin insights</title>
</svelte:head>

<div class="mx-auto flex w-full max-w-7xl flex-col gap-1 p-4 sm:p-6">
  {#if breadcrumbs}
    <Breadcrumbs label="Trilha de navegação" />
  {/if}
  <div id="conteudo" tabindex="-1" class="flex flex-col gap-6 outline-none">
    <div class="flex min-w-0 flex-col gap-1">
      <h1 class="text-xl font-semibold tracking-tight">{title}</h1>
      {#if description}
        <p class="max-w-prose text-sm text-base-content/70">{description}</p>
      {/if}
      {#if header}{@render header()}{/if}
    </div>
    {@render children()}
  </div>
</div>

<style>
  @container plinth-table (max-width: 40rem) {
    #conteudo :global(.plinth-table.has-card thead) {
      display: none;
    }
  }
</style>
