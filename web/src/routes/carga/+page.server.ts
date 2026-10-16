import { readDocument } from "$lib/server/site-data";
import type { Load } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => ({ load: await readDocument<Load>("load") });
