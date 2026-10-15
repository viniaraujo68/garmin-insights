import { error } from "@sveltejs/kit";
import { readDocument } from "$lib/server/site-data";
import type { ActivityDetail, ActivitySummary, Routes } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params }) => {
  if (!/^\d+$/.test(params.id)) error(404, "Corrida não encontrada");
  const activities = await readDocument<ActivitySummary[]>("activities");
  const runs = activities.filter((activity) => activity.sport === "run");
  const position = runs.findIndex((run) => run.activity_id === params.id);
  if (position < 0) error(404, "Corrida não encontrada");
  const [detail, routes] = await Promise.all([
    readDocument<ActivityDetail>(`activity/${params.id}`),
    readDocument<Routes>("routes"),
  ]);
  return {
    detail,
    privacy: routes.privacy,
    previousId: runs[position - 1]?.activity_id ?? null,
    nextId: runs[position + 1]?.activity_id ?? null,
  };
};
