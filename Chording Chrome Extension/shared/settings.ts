export interface ShorthandRule { pattern: string; replacement: string }
export interface Profile { id: string; name: string; rules: ShorthandRule[] }
export interface Settings { isEnabled: boolean; activeProfileId: string; profiles: Profile[] }
export type Command =
  | { type: "SET_ACTIVE_PROFILE"; profileId: string }
  | { type: "SET_ENABLED"; isEnabled: boolean }
  | { type: "CREATE_PROFILE"; profileName: string }
  | { type: "DELETE_PROFILE"; profileId: string }
  | { type: "UPDATE_PROFILE_RULES"; profileId: string; rules: ShorthandRule[]; expectedRules: ShorthandRule[] };
export type Response = { success: true; settings: Settings } | { success: false; error: string };
export function defaults(): Settings {
  return {
    isEnabled: true, activeProfileId: "default",
    profiles: [
      { id: "default", name: "Default", rules: [
        { pattern: "ty", replacement: "thank you" }, { pattern: "pls", replacement: "please" },
      ] },
      { id: "work", name: "Work", rules: [] },
      { id: "personal", name: "Personal", rules: [] },
    ],
  };
}
export function validateRules(value: unknown): asserts value is ShorthandRule[] {
  if (!Array.isArray(value)) throw new Error("Shortcuts must be a list.");
  const seen = new Set<string>();
  for (const rule of value) {
    if (!rule || typeof rule.pattern !== "string" || typeof rule.replacement !== "string")
      throw new Error("Every shortcut needs text and a replacement.");
    if (!rule.pattern || /\s/u.test(rule.pattern) || rule.pattern.length > 64)
      throw new Error("Use a shortcut of 1–64 characters, without spaces.");
    if (!rule.replacement.trim() || rule.replacement.length > 2000)
      throw new Error("Use a replacement of 1–2,000 characters.");
    if (seen.has(rule.pattern)) throw new Error('The shortcut "' + rule.pattern + '" already exists.');
    seen.add(rule.pattern);
  }
}
export function normalizeSettings(value: Record<string, unknown>): Settings {
  const initial = defaults();
  const profiles: Profile[] = [];
  const ids = new Set<string>();
  for (const candidate of Array.isArray(value.profiles) ? value.profiles : []) {
    if (!candidate || typeof candidate.id !== "string" || !candidate.id ||
        typeof candidate.name !== "string" || !candidate.name.trim() || ids.has(candidate.id)) continue;
    if (!Array.isArray(candidate.rules)) continue;
    ids.add(candidate.id);
    profiles.push({ id: candidate.id, name: candidate.name, rules: candidate.rules.filter(
      (rule: unknown): rule is ShorthandRule => !!rule && typeof rule === "object" &&
        "pattern" in rule && typeof rule.pattern === "string" &&
        "replacement" in rule && typeof rule.replacement === "string",
    ) });
  }
  if (!profiles.some(p => p.id === "default")) profiles.unshift(initial.profiles[0]);
  return {
    profiles,
    isEnabled: typeof value.isEnabled === "boolean" ? value.isEnabled : initial.isEnabled,
    activeProfileId: profiles.some(p => p.id === value.activeProfileId)
      ? value.activeProfileId as string : "default",
  };
}
export function applyCommand(settings: Settings, command: Command, makeId = () => crypto.randomUUID()): Settings {
  const next = structuredClone(settings);
  switch (command.type) {
    case "SET_ENABLED":
      if (typeof command.isEnabled !== "boolean") throw new Error("Choose whether shortcuts are enabled.");
      next.isEnabled = command.isEnabled;
      break;
    case "SET_ACTIVE_PROFILE":
      if (!next.profiles.some(p => p.id === command.profileId)) throw new Error("That profile no longer exists. Reload and try again.");
      next.activeProfileId = command.profileId;
      break;
    case "CREATE_PROFILE": {
      const name = typeof command.profileName === "string" ? command.profileName.trim() : "";
      if (!name || name.length > 80) throw new Error("Use a profile name of 1–80 characters.");
      if (next.profiles.some(p => p.name.toLocaleLowerCase() === name.toLocaleLowerCase()))
        throw new Error("A profile with that name already exists.");
      const id = makeId();
      next.profiles.push({ id, name, rules: [] });
      next.activeProfileId = id;
      break;
    }
    case "DELETE_PROFILE":
      if (command.profileId === "default") throw new Error("The Default profile cannot be deleted.");
      if (!next.profiles.some(p => p.id === command.profileId)) throw new Error("That profile no longer exists.");
      next.profiles = next.profiles.filter(p => p.id !== command.profileId);
      if (next.activeProfileId === command.profileId) next.activeProfileId = "default";
      break;
    case "UPDATE_PROFILE_RULES": {
      validateRules(command.rules);
      const profile = next.profiles.find(p => p.id === command.profileId);
      if (!profile) throw new Error("That profile no longer exists. Reload and try again.");
      if (JSON.stringify(profile.rules) !== JSON.stringify(command.expectedRules))
        throw new Error("These shortcuts changed in another window. Reload and try again.");
      profile.rules = structuredClone(command.rules);
      break;
    }
    default: throw new Error("Unknown settings action.");
  }
  // Chrome sync has an 8 KiB per-item quota; include the key and leave headroom.
  if (new TextEncoder().encode("profiles" + JSON.stringify(next.profiles)).length > 7500)
    throw new Error("Shortcut storage is full. Remove unused shortcuts or shorten replacements, then try again.");
  return next;
}
