<script lang="ts">
  import { SegmentedControl } from "@viniaraujo68/plinth/components";
  import MuscleMap from "$lib/components/MuscleMap.svelte";
  import PageFrame from "$lib/components/PageFrame.svelte";
  import PositionHeat from "$lib/components/PositionHeat.svelte";
  import TimeChart from "$lib/components/TimeChart.svelte";
  import { date, km, number } from "$lib/format";

  const { data } = $props();
  const sports = $derived(data.sports);
  let period = $state<"7d" | "28d">("28d");

  const NEAR_RETIREMENT_KM = 600;
  const RETIREMENT_KM = 800;
  const footballTotals = $derived({
    sessions: sports.football.length,
    minutes: sports.football.reduce((sum, session) => sum + (session.duration_min ?? 0), 0),
    sprints: sports.football.reduce((sum, session) => sum + session.sprints, 0),
  });
  const gearTone = (distance: number, limit: number | null): string => {
    const cap = limit ?? RETIREMENT_KM;
    if (distance >= cap) return "progress-error";
    if (distance >= Math.min(NEAR_RETIREMENT_KM, cap * 0.75)) return "progress-warning";
    return "progress-primary";
  };
</script>

<PageFrame
  title="Esportes"
  description="Futebol, academia e tênis. Tudo aqui depende de a atividade ser gravada no relógio."
>
  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="futebol">
    <div class="card-body gap-4 p-5">
      <div>
        <h2 id="futebol" class="text-base font-semibold">Futebol</h2>
        <p class="text-xs text-base-content/70">
          Piques são esforços acima de 18 km/h; alta velocidade é o que você correu acima de 15
          km/h.
        </p>
      </div>
      {#if sports.football.length}
        <div class="stats stats-horizontal bg-base-200/40">
          <div class="stat">
            <div class="stat-title">Jogos</div>
            <div class="stat-value text-2xl">{footballTotals.sessions}</div>
          </div>
          <div class="stat">
            <div class="stat-title">Minutos</div>
            <div class="stat-value text-2xl tabular-nums">{number(footballTotals.minutes)}</div>
          </div>
          <div class="stat">
            <div class="stat-title">Piques</div>
            <div class="stat-value text-2xl tabular-nums">{footballTotals.sprints}</div>
          </div>
        </div>
        <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {#each [...sports.football].reverse() as session (session.activity_id)}
            <article class="flex flex-col gap-2 rounded-box border border-base-content/10 p-4">
              <h3 class="font-semibold">{date(session.date)}</h3>
              <dl class="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <dt class="text-base-content/60">Tempo</dt>
                  <dd class="font-semibold tabular-nums">{number(session.duration_min)} min</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Distância</dt>
                  <dd class="font-semibold tabular-nums">{km(session.distance_km)}</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Carga</dt>
                  <dd class="font-semibold tabular-nums">{number(session.training_load)}</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Piques</dt>
                  <dd class="font-semibold tabular-nums">{session.sprints}</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Alta velocidade</dt>
                  <dd class="font-semibold tabular-nums">{number(session.high_speed_m)} m</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Vel. máxima</dt>
                  <dd class="font-semibold tabular-nums">
                    {number(session.max_speed_kmh, 1)} km/h
                  </dd>
                </div>
                <div>
                  <dt class="text-base-content/60">FC média</dt>
                  <dd class="font-semibold tabular-nums">{number(session.avg_hr)}</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Aeróbico</dt>
                  <dd class="font-semibold tabular-nums">{number(session.aerobic_te, 1)}</dd>
                </div>
                <div>
                  <dt class="text-base-content/60">Anaeróbico</dt>
                  <dd class="font-semibold tabular-nums">{number(session.anaerobic_te, 1)}</dd>
                </div>
              </dl>
              <PositionHeat positions={session.positions} />
            </article>
          {/each}
        </div>
      {:else}
        <div class="flex flex-col gap-1 rounded-box bg-base-200/50 p-4 text-sm">
          <p class="font-medium">Nenhum jogo registrado ainda.</p>
          <p class="text-base-content/70">
            No começo do jogo, inicie uma atividade no relógio (Futebol, se o seu modelo tiver;
            senão Cardio) e depois mude o tipo para futebol no Garmin Connect. Com a atividade
            gravada, a carga do jogo entra na Carga e aqui aparecem piques, velocidade e onde você
            jogou.
          </p>
        </div>
      {/if}
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="academia">
    <div class="card-body gap-4 p-5">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 id="academia" class="text-base font-semibold">Academia</h2>
          <p class="text-xs text-base-content/70">
            Séries por grupo muscular: o exercício principal conta inteiro e os auxiliares, metade.
          </p>
        </div>
        <SegmentedControl
          options={[
            { id: "7d", label: "7 dias" },
            { id: "28d", label: "28 dias" },
          ]}
          bind:value={period}
          label="Período"
          size="sm"
        />
      </div>
      {#if sports.gym.length}
        <MuscleMap muscles={sports.muscles} {period} />
        {#if sports.progress.length}
          <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {#each sports.progress as exercise (exercise.category)}
              <article class="rounded-box border border-base-content/10 p-4">
                <h3 class="text-sm font-semibold">{exercise.label} · 1RM estimado</h3>
                <TimeChart
                  series={[{ label: "1RM", points: exercise.points, slot: 6, dots: true }]}
                  format={(value) => `${number(value)} kg`}
                  ariaLabel="1RM estimado de {exercise.label}"
                  legend={false}
                  zero={false}
                  height="h-32"
                />
              </article>
            {/each}
          </div>
        {/if}
        <div class="overflow-x-auto">
          <table class="table table-sm">
            <thead
              ><tr
                ><th>Data</th><th class="text-right">Séries</th><th class="text-right"
                  >Repetições</th
                ><th class="text-right">Volume</th><th class="text-right">Carga</th></tr
              ></thead
            >
            <tbody>
              {#each [...sports.gym].reverse() as session (session.activity_id)}
                <tr>
                  <td>{date(session.date)}</td>
                  <td class="text-right tabular-nums">{session.sets}</td>
                  <td class="text-right tabular-nums">{number(session.reps)}</td>
                  <td class="text-right tabular-nums">{number(session.volume_kg)} kg</td>
                  <td class="text-right tabular-nums">{number(session.training_load)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <div class="flex flex-col gap-1 rounded-box bg-base-200/50 p-4 text-sm">
          <p class="font-medium">Nenhum treino de academia registrado ainda.</p>
          <p class="text-base-content/70">
            Use o perfil Musculação (ou Força) no relógio: ele conta séries e repetições sozinho.
            Confira e corrija os exercícios e pesos no app Garmin Connect depois do treino; com isso
            aparecem aqui o mapa muscular, o volume e a evolução do 1RM estimado.
          </p>
        </div>
      {/if}
    </div>
  </section>

  <section class="card border border-base-content/10 bg-base-100" aria-labelledby="tenis">
    <div class="card-body gap-4 p-5">
      <div>
        <h2 id="tenis" class="text-base font-semibold">Tênis</h2>
        <p class="text-xs text-base-content/70">
          Quilometragem de cada par. A partir de {NEAR_RETIREMENT_KM} km o amortecimento costuma cair;
          perto de {RETIREMENT_KM} km é hora de trocar.
        </p>
      </div>
      {#if sports.gear.length}
        <ul class="flex flex-col gap-3">
          {#each sports.gear as item (item.gear_id)}
            <li class="flex flex-col gap-1">
              <div class="flex justify-between text-sm">
                <span class="font-medium">{item.name}</span><span class="tabular-nums"
                  >{km(item.distance_km, 0)} de {km(item.max_km ?? RETIREMENT_KM, 0)}</span
                >
              </div>
              <progress
                class={["progress w-full", gearTone(item.distance_km, item.max_km)]}
                value={item.distance_km}
                max={item.max_km ?? RETIREMENT_KM}
              ></progress>
            </li>
          {/each}
        </ul>
      {:else}
        <div class="flex flex-col gap-1 rounded-box bg-base-200/50 p-4 text-sm">
          <p class="font-medium">Nenhum tênis cadastrado.</p>
          <p class="text-base-content/70">
            No Garmin Connect, vá em Equipamento e adicione o seu tênis como padrão para corrida:
            cada corrida passa a somar quilômetros nele.
          </p>
        </div>
      {/if}
    </div>
  </section>
</PageFrame>
