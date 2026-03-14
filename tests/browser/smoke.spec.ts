import { expect, test } from "@playwright/test";

test("login page is reachable", async ({ page, baseURL }) => {
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
