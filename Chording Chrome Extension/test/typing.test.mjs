import test from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import { expandAtCursor } from '../content/expansion.ts';
import { attachTypingSystem } from '../content/controller.ts';
import { defaults } from '../shared/settings.ts';

const rules = [{ pattern: 'ty', replacement: 'thank you' }];
test('expansion preserves punctuation, suffix and cursor position', () => {
  assert.deepEqual(expandAtCursor('Hello ty, world', 9, 9, rules),
    { value: 'Hello thank you, world', caret: 16 });
  assert.equal(expandAtCursor('plenty ', 7, 7, rules), null);
  assert.equal(expandAtCursor('ty ', 3, 1, rules), null);
  assert.equal(expandAtCursor('TY ', 3, 3, rules), null);
});

function fixture(markup = '<textarea></textarea>') {
  const dom = new JSDOM(markup);
  let settings = defaults();
  const detach = attachTypingSystem(dom.window.document, () => settings);
  const field = dom.window.document.querySelector('textarea, input');
  const type = (value, options = {}) => {
    field.value = value; field.setSelectionRange(value.length, value.length);
    field.dispatchEvent(new dom.window.InputEvent('input', { bubbles: true, inputType: 'insertText',
      data: value.slice(-1), ...options }));
  };
  return { dom, field, type, detach, pause: () => { settings.isEnabled = false; } };
}
test('typing expands once; immediate Backspace restores the original text', () => {
  const f = fixture();
  f.type('ty ');
  assert.equal(f.field.value, 'thank you ');
  const undo = new f.dom.window.KeyboardEvent('keydown', { key: 'Backspace', bubbles: true, cancelable: true });
  assert.equal(f.field.dispatchEvent(undo), false);
  assert.equal(f.field.value, 'ty ');
  f.detach(); f.dom.window.close();
});

test('paste, IME composition, paused state and detached listeners do not expand', () => {
  const f = fixture();
  f.type('ty ', { inputType: 'insertFromPaste' }); assert.equal(f.field.value, 'ty ');
  f.type('ty ', { isComposing: true }); assert.equal(f.field.value, 'ty ');
  f.pause(); f.type('ty '); assert.equal(f.field.value, 'ty ');
  f.detach(); f.type('ty '); assert.equal(f.field.value, 'ty ');
  f.dom.window.close();
});

test('protected fields and explicit opt-out are untouched', () => {
  for (const markup of ['<input type="text" autocomplete="one-time-code">',
    '<input type="text" autocomplete="section-login username">',
    '<textarea readonly></textarea>', '<div data-chordscribe="off"><textarea></textarea></div>']) {
    const f = fixture(markup);
    f.type('ty ');
    assert.equal(f.field.value, 'ty ');
    f.detach(); f.dom.window.close();
  }
});

test('editing after expansion clears the one-step undo', () => {
  const f = fixture();
  f.type('ty '); f.type('thank you x');
  const event = new f.dom.window.KeyboardEvent('keydown', { key: 'Backspace', bubbles: true, cancelable: true });
  assert.equal(f.field.dispatchEvent(event), true);
  assert.equal(f.field.value, 'thank you x');
  f.detach(); f.dom.window.close();
});
