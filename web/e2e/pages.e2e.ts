import { expect, test, type Page } from "@playwright/test";

const collectErrors = (page: Page): string[] => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && !message.text().includes("tile.openstreetmap.org"))
      errors.push(message.text());
  });
  return errors;
};

test("hoje mostra a prontidão e os cards", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Hoje", level: 1 })).toBeVisible();
  await expect(page.getByText("Prontidão para treinar")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Últimos 7 dias" })).toBeVisible();
  expect(errors).toEqual([]);
});

test("corridas mostra explorador, percursos e tabela", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/corridas");
  await expect(page.getByRole("heading", { name: "Explorador" })).toBeVisible();
  await expect(page.locator("canvas")).toHaveCount(1);
  await page.getByRole("button", { name: "Eficiência", exact: true }).click();
  await expect(page.getByText("Metros por batimento: subir é evoluir.")).toBeVisible();
  expect(await page.getByRole("img", { name: /Percurso da corrida/ }).count()).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("corrida sincroniza o hover entre as curvas e o mapa", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/corridas");
  await page.locator('a[href^="/corridas/"]').first().click();
  await expect(page.getByRole("heading", { name: "Percurso" })).toBeVisible();
  await expect(page.locator(".leaflet-container")).toBeVisible();
  const lane = page.getByRole("img", { name: "Pace ao longo da corrida" });
  await lane.scrollIntoViewIfNeeded();
  const box = await lane.boundingBox();
  if (!box) throw new Error("pace lane not rendered");
  await lane.hover({ position: { x: box.width * 0.4, y: box.height / 2 } });
  await expect(page.getByText(/^km \d+,\d{2}$/).first()).toBeVisible();
  await expect(page.locator(".map-wrap").getByText(/bpm/)).toBeVisible();
  await page.getByRole("button", { name: "Zona de FC", exact: true }).click();
  await expect(page.getByText(/^Z1 \d+–\d+$/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("corrida inexistente responde 404", async ({ page }) => {
  const response = await page.goto("/corridas/123");
  expect(response?.status()).toBe(404);
});

test("evolução mostra eficiência, provas e técnica", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/evolucao");
  await expect(page.getByRole("heading", { name: "Metros por batimento" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Previsões de prova" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Técnica no mesmo ritmo" })).toBeVisible();
  await page.getByRole("button", { name: "Como medido", exact: true }).click();
  await expect(page.getByRole("img", { name: "Eficiência por corrida" })).toBeVisible();
  expect(errors).toEqual([]);
});

test("carga mostra faixa ótima, frescor e calendário", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/carga");
  await expect(page.getByRole("heading", { name: "Carga aguda e a faixa ótima" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Calendário de treinos" })).toBeVisible();
  expect(await page.locator("canvas").count()).toBeGreaterThanOrEqual(5);
  expect(errors).toEqual([]);
});
