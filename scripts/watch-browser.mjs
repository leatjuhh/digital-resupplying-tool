import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { chromium } from "@playwright/test";

const endpoint = process.env.BROWSER_DEBUG_URL || "http://127.0.0.1:9222";
const defaultAppUrl = process.env.BROWSER_APP_URL || "http://127.0.0.1:3000";
const logDir = path.resolve(process.cwd(), "browser-artifacts");
const profileDir = path.resolve(process.cwd(), ".browser-debug-profile", "playwright");
const startedAt = new Date().toISOString().replace(/[:.]/g, "-");
const logPath = path.join(logDir, `watch-${startedAt}.log`);

fs.mkdirSync(logDir, { recursive: true });
fs.mkdirSync(profileDir, { recursive: true });

function writeLine(line) {
  const rendered = `${new Date().toISOString()} ${line}`;
  console.log(rendered);
  fs.appendFileSync(logPath, `${rendered}\n`, "utf8");
}

function formatLocation(page, suffix = "") {
  const url = page.url() || "(about:blank)";
  return suffix ? `[${url}] ${suffix}` : `[${url}]`;
}

function attachPage(page) {
  if (page.__drtAttached) {
    return;
  }

  page.__drtAttached = true;
  writeLine(`PAGE attached ${formatLocation(page)}`);

  page.on("console", async (message) => {
    const values = [];
    for (const arg of message.args()) {
      try {
        values.push(await arg.jsonValue());
      } catch {
        values.push("[unserializable]");
      }
    }

    const text = values.length > 0 ? JSON.stringify(values) : message.text();
    writeLine(`CONSOLE ${message.type().toUpperCase()} ${formatLocation(page, text)}`);
  });

  page.on("pageerror", (error) => {
    writeLine(`PAGEERROR ${formatLocation(page, error.stack || error.message)}`);
  });

  page.on("requestfailed", (request) => {
    const failureText = request.failure()?.errorText || "request failed";
    writeLine(`REQUESTFAILED ${formatLocation(page, `${request.method()} ${request.url()} :: ${failureText}`)}`);
  });

  page.on("response", async (response) => {
    if (response.status() < 400) {
      return;
    }

    writeLine(`RESPONSE ${formatLocation(page, `${response.status()} ${response.request().method()} ${response.url()}`)}`);
  });

  page.on("framenavigated", (frame) => {
    if (frame === page.mainFrame()) {
      writeLine(`NAVIGATED ${formatLocation(page)}`);
    }
  });
}

async function main() {
  let browser = null;
  let launchedContext = null;

  try {
    writeLine(`Connecting to ${endpoint}`);
    browser = await chromium.connectOverCDP(endpoint);
    writeLine("Connected to remote debug browser.");

    for (const context of browser.contexts()) {
      context.on("page", attachPage);
      for (const page of context.pages()) {
        attachPage(page);
      }
    }

    let context = browser.contexts()[0];
    if (!context) {
      context = await browser.newContext();
      context.on("page", attachPage);
    }

    if (context.pages().length === 0) {
      const page = await context.newPage();
      attachPage(page);
      await page.goto(defaultAppUrl, { waitUntil: "domcontentloaded" });
      writeLine(`OPENED ${defaultAppUrl}`);
    }
  } catch (error) {
    writeLine(`REMOTE unavailable, launching Playwright browser instead: ${error.message}`);
    launchedContext = await chromium.launchPersistentContext(profileDir, {
      headless: false,
      devtools: true,
      viewport: null,
      args: ["--start-maximized"],
    });

    launchedContext.on("page", attachPage);
    let page = launchedContext.pages()[0];
    if (!page) {
      page = await launchedContext.newPage();
    }
    attachPage(page);
    await page.goto(defaultAppUrl, { waitUntil: "domcontentloaded" });
    writeLine(`OPENED ${defaultAppUrl}`);
  }

  writeLine(`Watching browser events. Log file: ${logPath}`);
  writeLine("Press Ctrl+C to stop.");

  process.on("SIGINT", async () => {
    writeLine("Stopping browser watcher.");
    if (launchedContext) {
      await launchedContext.close();
    }
    if (browser) {
      await browser.close();
    }
    process.exit(0);
  });

  await new Promise(() => {});
}

main().catch((error) => {
  writeLine(`FATAL ${error.stack || error.message}`);
  process.exit(1);
});
