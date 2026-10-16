import { readDocument } from "$lib/server/site-data";
import type { Routes } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => ({ routes: await readDocument<Routes>("routes") });
