import type { RouteId } from "$app/types";
import type { RoutingConfig } from "@viniaraujo68/plinth/routing";

export const routes: RoutingConfig<RouteId> = {
  meta: {
    "/": { title: "Today", icon: "today" },
    "/day/[date]": { title: "Day" },
    "/runs": { title: "Runs", icon: "runs" },
    "/runs/[id]": { title: "Run" },
    "/progress": { title: "Progress", icon: "trend" },
    "/load": { title: "Load", icon: "load" },
    "/recovery": { title: "Recovery", icon: "recovery" },
    "/recovery/[night]": { title: "Night" },
    "/maps": { title: "Maps", icon: "map" },
  },

  pages: import.meta.glob("/src/routes/**/+page.svelte"),
};
