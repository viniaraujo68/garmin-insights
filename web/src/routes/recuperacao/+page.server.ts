import { loadRecovery } from "$lib/server/recovery";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = () => loadRecovery(null);
