<script lang="ts">
  import PageFrame from "$lib/components/PageFrame.svelte";
  import { GUIDE } from "$lib/guide";
</script>

<PageFrame
  title="Guia das métricas"
  description="O que cada número significa, como ler e o que costuma mexer nele. Faixas de referência são aproximadas e servem de orientação, não de diagnóstico."
>
  <nav class="flex flex-wrap gap-2" aria-label="Seções do guia">
    {#each GUIDE as section (section.id)}
      <a class="btn btn-ghost btn-sm" href="#{section.id}">{section.title}</a>
    {/each}
  </nav>
  {#each GUIDE as section (section.id)}
    <section
      id={section.id}
      class="card scroll-mt-4 border border-base-content/10 bg-base-100"
      aria-labelledby="{section.id}-title"
    >
      <div class="card-body gap-4 p-5">
        <h2 id="{section.id}-title" class="text-base font-semibold">{section.title}</h2>
        <dl class="grid gap-x-8 gap-y-4 md:grid-cols-2">
          {#each section.items as item (item.term)}
            <div class="flex flex-col gap-1 border-t border-base-content/10 pt-3">
              <dt class="font-medium">{item.term}</dt>
              <dd class="max-w-prose text-sm text-base-content/75">{item.text}</dd>
              {#if item.reference}<dd class="text-xs text-base-content/60 tabular-nums">
                  {item.reference}
                </dd>{/if}
            </div>
          {/each}
        </dl>
      </div>
    </section>
  {/each}
</PageFrame>
