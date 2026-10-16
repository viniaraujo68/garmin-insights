import { readDocument } from "$lib/server/site-data";
import type { Performance } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => ({
  performance: await readDocument<Performance>("performance"),
});
