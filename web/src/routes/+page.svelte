<script lang="ts">
  import PageFrame from "$lib/components/PageFrame.svelte";
  import { date, datetime, number } from "$lib/format";

  const { data } = $props();
</script>

<PageFrame title="Hoje" description="Base do projeto funcionando: dados lidos do pipeline.">
  <div class="stats border border-base-content/10 bg-base-100">
    <div class="stat">
      <div class="stat-title">Atividades</div>
      <div class="stat-value">{number(data.meta.activity_count)}</div>
      <div class="stat-desc">última em {date(data.meta.last_activity_date)}</div>
    </div>
    <div class="stat">
      <div class="stat-title">Dados de</div>
      <div class="stat-value text-2xl">
        {date(data.meta.first_day)} a {date(data.meta.last_day)}
      </div>
      <div class="stat-desc">gerado em {datetime(data.meta.generated_at)}</div>
    </div>
  </div>
</PageFrame>
