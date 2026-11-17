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

test("today shows readiness and cards", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Today", level: 1 })).toBeVisible();
  await expect(page.getByText("Training Readiness")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Last 7 days" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "The day in detail" })).toBeVisible();
  const heartRate = page.getByRole("img", { name: "HR over the day" });
  await heartRate.scrollIntoViewIfNeeded();
  const box = await heartRate.boundingBox();
  if (!box) throw new Error("heart rate lane not rendered");
  await heartRate.hover({ position: { x: box.width * 0.2, y: box.height / 2 } });
  await expect(page.locator("p").filter({ hasText: /^\s*\d{2}:\d{2}( · .+)?\s*$/ })).toBeVisible();
  expect(errors).toEqual([]);
});

test("runs shows explorer, routes and table", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/runs");
  await expect(page.getByRole("heading", { name: "Explorer" })).toBeVisible();
  await expect(page.locator("canvas")).toHaveCount(1);
  await page.getByRole("button", { name: "Efficiency", exact: true }).click();
  await expect(page.getByText("Metres per beat: going up means improving.")).toBeVisible();
  expect(await page.getByRole("img", { name: /Route of the run/ }).count()).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("run syncs hover between the lanes and the map", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/runs");
  await page.locator('a[href^="/runs/"]').first().click();
  await expect(page.getByRole("heading", { name: "Route" })).toBeVisible();
  await expect(page.locator(".leaflet-container")).toBeVisible();
  const lane = page.getByRole("img", { name: "Pace over the run" });
  await lane.scrollIntoViewIfNeeded();
  const box = await lane.boundingBox();
  if (!box) throw new Error("pace lane not rendered");
  await lane.hover({ position: { x: box.width * 0.4, y: box.height / 2 } });
  await expect(page.getByText(/^km \d+\.\d{2}$/).first()).toBeVisible();
  await expect(page.locator(".map-wrap").getByText(/bpm/)).toBeVisible();
  await page.getByRole("button", { name: "HR zone", exact: true }).click();
  await expect(page.getByText(/^Z1 \d+–\d+$/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("unknown run responds 404", async ({ page }) => {
  const response = await page.goto("/runs/123");
  expect(response?.status()).toBe(404);
});

test("progress shows efficiency, races and technique", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/progress");
  await expect(page.getByRole("heading", { name: "Metres per beat" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Race predictions" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Technique", exact: true })).toBeVisible();
  await expect(page.getByText("↓ lower is better").first()).toBeVisible();
  await page.getByRole("button", { name: "As measured", exact: true }).click();
  await expect(page.getByRole("img", { name: "Efficiency per run" })).toBeVisible();
  expect(errors).toEqual([]);
});

test("load shows the verdict, the volume and the range", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/load");
  await expect(page.getByTestId("load-summary").getByRole("heading", { level: 2 })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Kilometres per week" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Last 7 days load" })).toBeVisible();
  expect(await page.locator("canvas").count()).toBe(3);
  expect(errors).toEqual([]);
});

test("recovery shows trends, hypnogram and month", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/recovery");
  await expect(page.getByRole("heading", { name: "Overnight HRV" })).toBeVisible();
  await expect(page.getByRole("img", { name: "Sleep stages over the night" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Month at a glance" })).toBeVisible();
  await page.getByRole("button", { name: "4 weeks", exact: true }).click();
  await expect(
    page
      .getByRole("navigation", { name: "Main navigation" })
      .getByRole("link", { name: "Recovery" }),
  ).toBeVisible();
  const response = await page.goto("/recovery/2026-09-01");
  expect(response?.status()).toBe(200);
  await expect(page.getByText(/Slept \d{2}:\d{2}/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("maps draws all runs and switches the colour", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/maps");
  await expect(page.locator(".leaflet-container")).toBeVisible();
  await page.getByRole("button", { name: "Pace", exact: true }).click();
  await expect(page.getByText(/\(fast\)/)).toBeVisible();
  expect(errors).toEqual([]);
});

test("today navigates to other days", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Today", level: 1 })).toBeVisible();
  await page.getByRole("link", { name: "← previous day" }).click();
  await expect(page).toHaveURL(/\/day\/\d{4}-\d{2}-\d{2}$/);
  await expect(page.getByRole("link", { name: "next day →" })).toBeVisible();
  await expect(page.getByRole("heading", { level: 1 })).not.toHaveText("Today");
  const response = await page.goto("/day/2026-09-01");
  expect(response?.status()).toBe(200);
  await expect(page.getByText("Training Readiness")).toBeVisible();
  expect(errors).toEqual([]);
  const missing = await page.goto("/day/2020-01-01");
  expect(missing?.status()).toBe(404);
});
