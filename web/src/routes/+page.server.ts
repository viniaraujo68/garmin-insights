import { loadDay } from "$lib/server/day";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = () => loadDay(null);
