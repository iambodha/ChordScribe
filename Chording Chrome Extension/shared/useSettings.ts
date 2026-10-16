import { useCallback, useEffect, useRef, useState } from "react";
import { readSettings, sendCommand } from "./storage.ts";
import type { Settings, Command } from "./settings.ts";
export function useSettings() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const revision = useRef(0);
  const reload = useCallback(async () => {
    const request = ++revision.current;
    try {
      const next = await readSettings();
      if (request === revision.current) { setSettings(next); setError(""); }
    }
    catch { if (request === revision.current) setError("Could not load settings. Reload the extension and try again."); }
  }, []);
  useEffect(() => {
    void reload();
    const change = (_: unknown, area: string) => { if (area === "sync") void reload(); };
    chrome.storage.onChanged.addListener(change);
    return () => chrome.storage.onChanged.removeListener(change);
  }, [reload]);
  const save = async (command: Command): Promise<boolean> => {
    if (pending.current) return false;
    pending.current = true;
    setBusy(true); setError("");
    try { const next = await sendCommand(command); ++revision.current; setSettings(next); return true; }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Could not save. Please try again."); return false; }
    finally { pending.current = false; setBusy(false); }
  };
  return { settings, error, busy, save, reload };
}
