import { readFile, writeFile } from "node:fs/promises";
import { compile } from "json-schema-to-typescript";

const SCHEMA_PATH = new URL("../src/lib/data/schema.json", import.meta.url);
const TYPES_PATH = new URL("../src/lib/data/types.ts", import.meta.url);

const stripPropertyTitles = (node) => {
  if (Array.isArray(node)) return node.map(stripPropertyTitles);
  if (node === null || typeof node !== "object") return node;
  const copy = Object.fromEntries(
    Object.entries(node).map(([key, value]) => [key, stripPropertyTitles(value)]),
  );
  if (copy.properties)
    for (const property of Object.values(copy.properties)) {
      delete property.title;
      for (const option of property.anyOf ?? []) delete option.title;
    }
  return copy;
};

const schemas = stripPropertyTitles(JSON.parse(await readFile(SCHEMA_PATH, "utf8")));
const seen = new Set();
const chunks = [];
for (const schema of Object.values(schemas)) {
  const definitions = { ...(schema.$defs ?? {}) };
  delete schema.$defs;
  for (const [name, definition] of [[schema.title, schema], ...Object.entries(definitions)]) {
    if (seen.has(name)) continue;
    seen.add(name);
    const standalone = { ...definition, title: name, $defs: definitions };
    const source = await compile(standalone, name, {
      bannerComment: "",
      additionalProperties: false,
      declareExternallyReferenced: false,
      format: false,
    });
    chunks.push(source.trim());
  }
}
await writeFile(TYPES_PATH, `${chunks.join("\n\n")}\n`);
console.log(`wrote ${chunks.length} types to ${TYPES_PATH.pathname}`);
