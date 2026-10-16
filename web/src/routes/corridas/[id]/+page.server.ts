import { error } from "@sveltejs/kit";
import { readDocument } from "$lib/server/site-data";
import type { ActivityDetail, ActivitySummary } from "$lib/data/types";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params }) => {
  if (!/^\d+$/.test(params.id)) error(404, "Corrida não encontrada");
  const activities = await readDocument<ActivitySummary[]>("activities");
  const runs = activities.filter((activity) => activity.sport === "run");
  const position = runs.findIndex((run) => run.activity_id === params.id);
  if (position < 0) error(404, "Corrida não encontrada");
  return {
    detail: await readDocument<ActivityDetail>(`activity/${params.id}`),
    previousId: runs[position - 1]?.activity_id ?? null,
    nextId: runs[position + 1]?.activity_id ?? null,
  };
};
