import { readDocument } from "$lib/server/site-data";
import type { ActivitySummary, Routes } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => {
  const [activities, routes] = await Promise.all([
    readDocument<ActivitySummary[]>("activities"),
    readDocument<Routes>("routes"),
  ]);
  return { runs: activities.filter((activity) => activity.sport === "run"), routes };
};
