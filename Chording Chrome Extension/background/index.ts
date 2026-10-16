import { applyCommand, normalizeSettings, type Command } from "../shared/settings.ts";
// Serialize read/modify/write operations so simultaneous popup/options edits do not
// overwrite each other. Reread storage after every operation, including failures.
let pending: Promise<unknown> = Promise.resolve();
chrome.runtime.onInstalled.addListener(() => {
  pending = pending.catch(() => {}).then(async () => {
    const existing = await chrome.storage.sync.get(["profiles", "activeProfileId", "isEnabled"]);
    await chrome.storage.sync.set(normalizeSettings(existing));
    await chrome.storage.sync.remove("typingHistory");
  });
  void pending.catch(error => console.error("ChordScribe could not initialize settings.", error));
});
chrome.runtime.onMessage.addListener((message: Command, sender, sendResponse) => {
  // Content scripts only read settings; mutations belong to extension pages.
  if (!sender.url?.startsWith(chrome.runtime.getURL("")) || sender.tab) return false;
  const operation = pending.catch(() => {}).then(async () => {
    const current = normalizeSettings(await chrome.storage.sync.get(["profiles", "activeProfileId", "isEnabled"]));
    const next = applyCommand(current, message);
    await chrome.storage.sync.set(next);
    return next;
  });
  pending = operation;
  void operation.then(
    settings => sendResponse({ success: true, settings }),
    error => sendResponse({ success: false, error: error instanceof Error ? error.message : "Could not save settings." }),
  );
  return true;
});
