import type { ShorthandRule } from "../shared/settings.ts";
export interface Expansion { value: string; caret: number }
export function expandAtCursor(value: string, start: number, end: number, rules: ShorthandRule[]): Expansion | null {
  if (start !== end || start < 1 || start > value.length) return null;
  const match = /(^|\s)(\S+)([\s.,!?;:])$/u.exec(value.slice(0, start));
  if (!match) return null;
  const rule = rules.find(rule => rule.pattern === match[2]);
  if (!rule) return null;
  const from = start - match[2].length - match[3].length;
  return {
    value: value.slice(0, from) + rule.replacement + match[3] + value.slice(start),
    caret: from + rule.replacement.length + match[3].length,
  };
}
