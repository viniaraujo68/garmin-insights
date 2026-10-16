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
  await expect(page.getByRole("heading", { name: "O dia em detalhe" })).toBeVisible();
  const heartRate = page.getByRole("img", { name: "FC ao longo do dia" });
  await heartRate.scrollIntoViewIfNeeded();
  const box = await heartRate.boundingBox();
  if (!box) throw new Error("heart rate lane not rendered");
  await heartRate.hover({ position: { x: box.width * 0.2, y: box.height / 2 } });
  await expect(page.locator("p").filter({ hasText: /^\s*\d{2}:\d{2}( · .+)?\s*$/ })).toBeVisible();
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

test("carga mostra faixa ótima, frescor e intensidade", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/carga");
  await expect(page.getByRole("heading", { name: "Carga aguda e a faixa ótima" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Leve × forte por semana" })).toBeVisible();
  expect(await page.locator("canvas").count()).toBeGreaterThanOrEqual(5);
  expect(errors).toEqual([]);
});

test("recuperação mostra tendências, hipnograma e mês", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/recuperacao");
  await expect(page.getByRole("heading", { name: "VFC da noite" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Fases do sono ao longo da noite" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Mês num relance" })).toBeVisible();
  await page.getByRole("button", { name: "4 semanas", exact: true }).click();
  await expect(
    page
      .getByRole("navigation", { name: "Navegação principal" })
      .getByRole("link", { name: "Recuperação" }),
  ).toBeVisible();
  const response = await page.goto("/recuperacao/2026-09-01");
  expect(response?.status()).toBe(200);
  await expect(page.getByText(/Dormiu \d{2}:\d{2}/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("mapas desenha todas as corridas e troca a cor", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/mapas");
  await expect(page.locator(".leaflet-container")).toBeVisible();
  await page.getByRole("button", { name: "Pace", exact: true }).click();
  await expect(page.getByText(/\(rápido\)/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("hoje navega para outros dias", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Hoje", level: 1 })).toBeVisible();
  await page.getByRole("link", { name: "← dia anterior" }).click();
  await expect(page).toHaveURL(/\/dia\/\d{4}-\d{2}-\d{2}$/);
  await expect(page.getByRole("link", { name: "próximo dia →" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 1 })).not.toHaveText("Hoje");
  const response = await page.goto("/dia/2026-09-01");
  expect(response?.status()).toBe(200);
  await expect(page.getByText("Prontidão para treinar")).toBeVisible();
  expect(errors).toEqual([]);
  const missing = await page.goto("/dia/2020-01-01");
  expect(missing?.status()).toBe(404);
});
