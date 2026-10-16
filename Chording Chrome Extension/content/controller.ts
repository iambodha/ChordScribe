import { expandAtCursor } from "./expansion.ts";
import type { Settings } from "../shared/settings.ts";
type Field = HTMLInputElement | HTMLTextAreaElement;
interface Undo { before: string; after: string; beforeCaret: number; afterCaret: number }
export function attachTypingSystem(doc: Document, settings: () => Settings | null): () => void {
  const win = doc.defaultView! as Window & typeof globalThis;
  const undo = new WeakMap<Field, Undo>();
  let applying = false;
  function field(event: Event): Field | null {
    const element = event.target;
    if (!(element instanceof win.HTMLTextAreaElement) &&
        !(element instanceof win.HTMLInputElement && ["text", "search"].includes(element.type))) return null;
    if (element.disabled || element.readOnly || element.closest("[data-chordscribe='off']") ||
        /password|one-time-code|cc-|username/i.test(element.autocomplete)) return null;
    return element;
  }
  function replace(target: Field, value: string, caret: number) {
    const prototype = target instanceof win.HTMLTextAreaElement ? win.HTMLTextAreaElement.prototype : win.HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(prototype, "value")!.set!.call(target, value);
    target.setSelectionRange(caret, caret);
    applying = true;
    try { target.dispatchEvent(new win.InputEvent("input", { bubbles: true, inputType: "insertReplacementText" })); }
    finally { applying = false; }
  }
  const input = (event: Event) => {
    if (applying) return;
    const target = field(event);
    if (!target) return;
    undo.delete(target);
    const state = settings();
    const typed = event as InputEvent;
    if (!state?.isEnabled || typed.isComposing || typed.inputType !== "insertText" ||
        typed.data === null || Array.from(typed.data).length !== 1 ||
        target.selectionStart === null || target.selectionEnd === null) return;
    const profile = state.profiles.find(p => p.id === state.activeProfileId);
    if (!profile) return;
    const result = expandAtCursor(target.value, target.selectionStart, target.selectionEnd, profile.rules);
    if (!result) return;
    const previous = { before: target.value, after: result.value, beforeCaret: target.selectionStart, afterCaret: result.caret };
    replace(target, result.value, result.caret);
    if (target.value === result.value) undo.set(target, previous);
  };
  const keydown = (event: Event) => {
    const key = event as KeyboardEvent;
    const target = field(event);
    if (!target || !settings()?.isEnabled || key.isComposing || key.ctrlKey || key.metaKey || key.altKey) return;
    const previous = undo.get(target);
    if (key.key === "Backspace" && previous && target.value === previous.after &&
        target.selectionStart === previous.afterCaret && target.selectionEnd === previous.afterCaret) {
      key.preventDefault();
      replace(target, previous.before, previous.beforeCaret);
      undo.delete(target);
    } else if (key.key !== "Shift") undo.delete(target);
  };
  const clearUndo = (event: Event) => { const target = field(event); if (target) undo.delete(target); };
  doc.addEventListener("input", input);
  doc.addEventListener("keydown", keydown);
  doc.addEventListener("pointerdown", clearUndo);
  return () => {
    doc.removeEventListener("input", input);
    doc.removeEventListener("keydown", keydown);
    doc.removeEventListener("pointerdown", clearUndo);
  };
}
