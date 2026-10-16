import { error } from "@sveltejs/kit";
import { readDocument } from "$lib/server/site-data";
import type { ActivitySummary, Meta, Today } from "$lib/data/types";

export const loadDay = async (requested: string | null) => {
  const meta = await readDocument<Meta>("meta");
  if (requested !== null && !meta.days.includes(requested)) error(404, "Dia sem dados");
  const day = requested ?? meta.days.at(-1);
  if (!day) error(503, "Ainda não há dias sincronizados");
  const [today, activities] = await Promise.all([
    readDocument<Today>(`day/${day}`),
    readDocument<ActivitySummary[]>("activities"),
  ]);
  const position = meta.days.indexOf(day);
  return {
    meta,
    today,
    lastActivity:
      activities.find((activity) => activity.activity_id === today.last_activity_id) ?? null,
    previousDay: meta.days[position - 1] ?? null,
    nextDay: meta.days[position + 1] ?? null,
  };
};
