import type { RouteId } from "$app/types";
import type { RoutingConfig } from "@viniaraujo68/plinth/routing";

export const routes: RoutingConfig<RouteId> = {
  meta: {
    "/": { title: "Hoje", icon: "today" },
    "/dia/[data]": { title: "Dia" },
    "/corridas": { title: "Corridas", icon: "runs" },
    "/corridas/[id]": { title: "Corrida" },
    "/evolucao": { title: "Evolução", icon: "trend" },
    "/carga": { title: "Carga", icon: "load" },
    "/recuperacao": { title: "Recuperação", icon: "recovery" },
    "/recuperacao/[noite]": { title: "Noite" },
    "/mapas": { title: "Mapas", icon: "map" },
  },

  pages: import.meta.glob("/src/routes/**/+page.svelte"),
};
