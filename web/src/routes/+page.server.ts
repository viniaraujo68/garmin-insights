import { readDocument } from "$lib/server/site-data";
import type { ActivitySummary, Meta } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => ({
  meta: await readDocument<Meta>("meta"),
  activities: await readDocument<ActivitySummary[]>("activities"),
});
