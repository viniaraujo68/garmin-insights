import { readDocument } from "$lib/server/site-data";
import type { ActivitySummary, Meta, Today } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => {
  const [meta, today, activities] = await Promise.all([
    readDocument<Meta>("meta"),
    readDocument<Today>("today"),
    readDocument<ActivitySummary[]>("activities"),
  ]);
  const lastActivity =
    activities.find((activity) => activity.activity_id === today.last_activity_id) ?? null;
  return { meta, today, lastActivity };
};
