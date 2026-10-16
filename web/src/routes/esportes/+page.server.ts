import { readDocument } from "$lib/server/site-data";
import type { Sports } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => ({ sports: await readDocument<Sports>("sports") });
