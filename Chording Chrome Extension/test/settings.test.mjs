import test from 'node:test';
import assert from 'node:assert/strict';
import { defaults, normalizeSettings, validateRules, applyCommand } from '../shared/settings.ts';

test('an upgrade preserves profiles, pause state and active profile', () => {
  const old = { profiles: [{ id: 'mine', name: 'My work', rules: [{ pattern: 'brb', replacement: 'be right back' }] }],
    isEnabled: false, activeProfileId: 'mine', typingHistory: { secret: 'ignored' } };
  const next = normalizeSettings(old);
  assert.equal(next.isEnabled, false);
  assert.equal(next.activeProfileId, 'mine');
  assert.deepEqual(next.profiles[1], old.profiles[0]);
  assert.equal('typingHistory' in next, false);
});

test('default settings include the documented example shortcuts', () => {
  const settings = normalizeSettings({});
  assert.equal(settings.activeProfileId, 'default');
  assert.equal(settings.isEnabled, true);
  assert.deepEqual(settings.profiles[0].rules, defaults().profiles[0].rules);
});

test('profile operations preserve unrelated profiles and protect Default', () => {
  const original = defaults();
  const created = applyCommand(original, { type: 'CREATE_PROFILE', profileName: ' Research ' }, () => 'research');
  assert.equal(created.activeProfileId, 'research');
  assert.equal(original.profiles.length, 3);
  assert.equal(created.profiles[3].name, 'Research');
  const deleted = applyCommand(created, { type: 'DELETE_PROFILE', profileId: 'research' });
  assert.equal(deleted.activeProfileId, 'default');
  assert.throws(() => applyCommand(original, { type: 'DELETE_PROFILE', profileId: 'default' }), /cannot be deleted/);
  assert.throws(() => applyCommand(original, { type: 'CREATE_PROFILE', profileName: 'default' }), /already exists/);
});

test('invalid, duplicate and over-quota shortcuts fail before saving', () => {
  assert.throws(() => validateRules([{ pattern: 'two words', replacement: 'phrase' }]), /without spaces/);
  assert.throws(() => validateRules([{ pattern: 'x', replacement: ' ' }]), /replacement/);
  assert.throws(() => validateRules([{ pattern: 'x', replacement: 'a' }, { pattern: 'x', replacement: 'b' }]), /already exists/);
  const settings = defaults();
  assert.throws(() => applyCommand(settings, { type: 'UPDATE_PROFILE_RULES', profileId: 'default',
    expectedRules: settings.profiles[0].rules,
    rules: Array.from({ length: 6 }, (_, i) => ({ pattern: 'x' + i, replacement: 'a'.repeat(1500) })) }), /storage is full/);
});

test('a stale editor cannot overwrite newer shortcuts', () => {
  const settings = defaults();
  assert.throws(() => applyCommand(settings, { type: 'UPDATE_PROFILE_RULES', profileId: 'default',
    expectedRules: [], rules: [] }), /another window/);
});
