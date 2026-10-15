import type { RouteId } from "$app/types";
import type { RoutingConfig } from "@viniaraujo68/plinth/routing";

export const routes: RoutingConfig<RouteId> = {
  meta: {
    "/": { title: "Hoje", icon: "today" },
    "/corridas": { title: "Corridas", icon: "runs" },
    "/corridas/[id]": { title: "Corrida" },
  },

  pages: import.meta.glob("/src/routes/**/+page.svelte"),
};
