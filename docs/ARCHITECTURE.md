# Architecture

## Extension

```text
Popup / options
    -> validated command -> background service worker
    -> serialized read / modify / write -> Chrome sync settings
    -> storage change -> popup, options, content script refresh

Input event -> supported-field check -> exact shortcut at caret
    -> native value setter + input event -> in-memory one-step undo
```

`shared/settings.ts` contains the settings schema, migration defaults, validation,
and pure command handling. The background serializes edits within its service-worker
instance, checks the sender, and reports save failures. Shortcut updates include
the previously read rules, so a stale editor cannot silently replace newer rules.
Cross-device Chrome sync still follows Chrome's conflict behavior; this is not a
distributed transaction system.

The content controller accepts single-character typing events, skips composition
and paste, and preserves the suffix and caret when replacing text. Backspace can
undo the immediately preceding expansion. Later input, navigation, or pointer
interaction clears that undo opportunity. No dictionary-based autocorrection or
global keyboard hook is used.

The React popup and options share loading, save, error, and storage-refresh logic.
The build bundles all code locally; the output contains no external script imports.

## Layout research engine

The existing key mappings, effort metrics and scoring are retained. The worker
pool is scoped to a comparison/search instance, bounded to four workers, and must
be closed after use. It starts lazily and propagates failures to its caller.

`Runner` rejects empty input, invalid effort limits/penalties and a corpus that
cannot advance the effort model. The default sample is loaded relative to the
repository, rather than by scanning the current directory and installed packages.

`scripts/benchmark.cjs` evaluates fixed presets with a recorded corpus hash and
effort budget. Genetic search retains its existing stochastic mutation and
selection process. Historical Python/data scripts are not imported by the
supported runtime.

## Verification boundaries

Node tests exercise the real settings reducer, text-expansion controller in a DOM,
the legacy scorer, worker isolation, error propagation, and input guards.
The local browser preview simulates Chrome storage and messaging. It cannot prove
installation, browser service-worker behavior, sync across devices, or every
third-party site's handling of synthetic input events; verify those in Chrome.
