import { readFile } from "node:fs/promises";
import path from "node:path";
import { error } from "@sveltejs/kit";
import { env } from "$env/dynamic/private";

const siteDir = (): string => path.resolve(env.PASSADA_SITE_DIR ?? "../data/site");

export const readDocument = async <T>(name: string): Promise<T> => {
  const file = path.join(siteDir(), `${name}.json`);
  try {
    return JSON.parse(await readFile(file, "utf8")) as T;
  } catch (cause) {
    if ((cause as NodeJS.ErrnoException).code === "ENOENT")
      error(
        503,
        `Dados não encontrados em ${file}. Rode o pipeline: cd pipeline && uv run --frozen python -m passada.run`,
      );
    throw cause;
  }
};

export const readOptionalDocument = async <T>(name: string): Promise<T | null> => {
  try {
    return JSON.parse(await readFile(path.join(siteDir(), `${name}.json`), "utf8")) as T;
  } catch (cause) {
    if ((cause as NodeJS.ErrnoException).code === "ENOENT") return null;
    throw cause;
  }
};
