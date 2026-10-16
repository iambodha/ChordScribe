import { normalizeSettings, type Settings, type Command, type Response } from "./settings.ts";
export async function readSettings(): Promise<Settings> {
  return normalizeSettings(await chrome.storage.sync.get(["profiles", "activeProfileId", "isEnabled"]));
}
export async function sendCommand(command: Command): Promise<Settings> {
  const response: Response | undefined = await chrome.runtime.sendMessage(command);
  if (!response?.success) throw new Error(response?.error || "Could not save. Reload the extension and try again.");
  return response.settings;
}
