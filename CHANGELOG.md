# Changelog

## 0.2.0 — runnable project cleanup

- Added root npm workspaces, a lockfile, build scripts, a Manifest V3 manifest,
  local browser playground, and reproducible extension ZIP packaging.
- Completed popup/settings flows with profile creation, explicit shortcut editing,
  validation, pause, recoverable errors, and one-step Backspace undo.
- Preserved saved profiles on extension updates and removed typing-history storage.
- Scoped expansion to ordinary text/search inputs and text areas; rich-text/IME/paste
  behavior is explicitly outside the supported expansion path.
- Added a bundled corpus, deterministic layout comparison output and input guards.
- Isolated and bounded layout workers; added explicit cleanup and error propagation.
- Restored actual test execution. Corrected stale legacy result snapshots against
  the unchanged main@99f722d runner before adding regression coverage.
- Documented the 18% mean improvement from real testing with 15 participants,
  alongside method and limitations. Added credits and historical-script status.
- Added CI checks and downloadable build artifacts.

The extension changes have not been used to repeat the original participant study.
