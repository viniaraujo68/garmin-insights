import { error } from "@sveltejs/kit";
import { readDocument } from "$lib/server/site-data";
import type { Meta, Recovery, SleepNight } from "$lib/data/types";

export const loadRecovery = async (requested: string | null) => {
  const [recovery, meta] = await Promise.all([
    readDocument<Recovery>("recovery"),
    readDocument<Meta>("meta"),
  ]);
  const dates = recovery.nights.map((night) => night.date);
  if (requested !== null && !dates.includes(requested)) error(404, "Noite não encontrada");
  const chosen = requested ?? dates.at(-1) ?? null;
  const night = chosen ? await readDocument<SleepNight>(`sleep/${chosen}`) : null;
  return { recovery, night, today: meta.today };
};
