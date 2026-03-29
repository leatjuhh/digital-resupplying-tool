import { expect, test, type BrowserContext, type Page } from "@playwright/test";

async function clearSession(page: Page, context: BrowserContext, baseURL: string) {
  await context.clearCookies();
  await page.goto(`${baseURL}/login`, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });
}

async function login(page: Page, context: BrowserContext, baseURL: string, username: string, password: string) {
  await clearSession(page, context, baseURL);
  await page.goto(`${baseURL}/login`, { waitUntil: "networkidle" });

  await page.getByLabel("Gebruikersnaam").fill(username);
  await page.getByLabel("Wachtwoord").fill(password);
  await page.getByRole("button", { name: "Inloggen" }).click();
  await page.waitForURL(`${baseURL}/`, { timeout: 15_000 });
}

test("login page is reachable", async ({ page, baseURL }) => {
  await page.context().clearCookies();
  await page.addInitScript(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });
  await page.goto(`${baseURL}/login`, { waitUntil: "networkidle" });

  await expect(page.getByText("Digital Resupplying Tool")).toBeVisible();
  await expect(page.getByLabel("Gebruikersnaam")).toBeVisible();
  await expect(page.getByLabel("Wachtwoord")).toBeVisible();
});

test("backend health endpoint responds", async ({ request }) => {
  const backendUrl = process.env.PLAYWRIGHT_BACKEND_URL || "http://127.0.0.1:8000";
  const response = await request.get(`${backendUrl}/health`);

  expect(response.ok()).toBeTruthy();
  await expect(response.json()).resolves.toEqual({ status: "healthy" });
});

test("admin dashboard shows live summary and links to proposals", async ({ page, baseURL, context }) => {
  await login(page, context, baseURL!, "admin", "Admin123!");

  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Live totaal")).toBeVisible();
  await expect(page.getByText("Totaal Voorstellen")).toBeVisible();
  await expect(page.getByText("Wachtend op Beoordeling")).toBeVisible();
  await expect(page.getByText("Open Opdrachten")).toBeVisible();
  await expect(page.getByText("Actieve Winkels")).toBeVisible();

  await page.getByRole("link", { name: "Alle bekijken" }).click();
  await page.waitForURL(`${baseURL}/proposals`, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Herverdelingsvoorstellen" })).toBeVisible();
  await expect(page.getByText("Externe Algoritmestatus")).toBeVisible();
});

test("admin sees all settings tabs on real settings page", async ({ page, baseURL, context }) => {
  await login(page, context, baseURL!, "admin", "Admin123!");

  await expect(page.getByText("DRT")).toBeVisible();
  await page.goto(`${baseURL}/settings`, { waitUntil: "networkidle" });
  await page.waitForURL(`${baseURL}/settings`, { timeout: 15_000 });

  await expect(page.getByRole("tab", { name: "Algemeen" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Regels" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Gebruikers" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Rollen" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "API" })).toBeVisible();

  await page.getByRole("tab", { name: "Gebruikers" }).click();
  await expect(page.getByRole("button", { name: /Nieuwe Gebruiker/i })).toBeVisible();

  await page.getByRole("tab", { name: "Rollen" }).click();
  await expect(page.getByRole("button", { name: /Permissies Opslaan/i })).toBeVisible();
});

test("user sees only allowed settings tabs and rule editing remains enabled", async ({ page, baseURL, context }) => {
  await login(page, context, baseURL!, "user", "User123!");

  await page.goto(`${baseURL}/settings`, { waitUntil: "networkidle" });
  await page.waitForURL(`${baseURL}/settings`, { timeout: 15_000 });
  await expect(page.getByRole("tab", { name: "Algemeen" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Regels" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Gebruikers" })).toHaveCount(0);
  await expect(page.getByRole("tab", { name: "Rollen" })).toHaveCount(0);
  await expect(page.getByRole("tab", { name: "API" })).toHaveCount(0);

  await expect(page.getByRole("button", { name: "Instellingen Opslaan" })).toBeDisabled();

  await page.getByRole("tab", { name: "Regels" }).click();
  await expect(page.getByRole("button", { name: "Regels Opslaan" })).toBeEnabled();
});

test("dashboard shows real summary sections for admin", async ({ page, baseURL, context }) => {
  await login(page, context, baseURL!, "admin", "Admin123!");

  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Wachtende Reeksen", { exact: true })).toBeVisible();
  await expect(page.getByText("Recente Activiteit", { exact: true })).toBeVisible();
  await expect(page.getByText("Aandachtspunten", { exact: true })).toBeVisible();
  await expect(page.getByText("Live totaal", { exact: true })).toBeVisible();
});

test("store user can open assignments and is redirected away from settings", async ({ page, baseURL, context }) => {
  await login(page, context, baseURL!, "store", "Store123!");

  await expect(page.getByRole("link", { name: /Opdrachten/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /Instellingen/i })).toHaveCount(0);

  await page.goto(`${baseURL}/assignments`, { waitUntil: "networkidle" });
  await page.waitForURL(`${baseURL}/assignments`, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: /Mijn Opdrachten/i })).toBeVisible();
  await expect(page.getByRole("columnheader", { name: /Reeks ID/i })).toBeVisible();

  await page.goto(`${baseURL}/settings`, { waitUntil: "networkidle" });
  await page.waitForURL(`${baseURL}/`, { timeout: 15_000 });
});
