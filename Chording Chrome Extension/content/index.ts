import { readSettings } from "../shared/storage.ts";
import { attachTypingSystem } from "./controller.ts";
import type { Settings } from "../shared/settings.ts";
let settings: Settings | null = null;
let revision = 0;
async function reload() {
  const request = ++revision;
  try {
    const next = await readSettings();
    if (request === revision) settings = next;
  } catch { if (request === revision) settings = null; }
}
void reload();
attachTypingSystem(document, () => settings);
chrome.storage.onChanged.addListener((_, area) => { if (area === "sync") void reload(); });
