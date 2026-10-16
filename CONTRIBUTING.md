# Contributing

Use Node.js 24 or newer. Install the root workspace once with `npm ci`; the
root `package-lock.json` is the dependency source of truth.

Before opening a pull request:

```bash
npm run check
npm run benchmark
npm run package
```

For expansion/settings changes, run `npm run preview` and check the popup,
profile selection, new/edit/delete shortcut flows, duplicate validation, pause,
immediate Backspace undo, and a narrow settings viewport. Then load the real
extension using the README steps and verify on ordinary input and textarea fields.

Do not test in a form that will submit private information. Use synthetic phrases.
Check that paste, composition, password fields, protected autocomplete fields and
read-only inputs stay unchanged. After editing a saved rule in two settings tabs,
a stale edit should show a recoverable error rather than overwrite the first save.

Keep research results traceable. A simulator result needs a corpus hash and
settings; a human-study result needs its method and sample size. Never describe a
model score as a measured human typing-speed result.

Preserve the historical Python experiments unless the change specifically concerns
them. Do not commit downloaded corpora, participant records, local settings,
`node_modules`, or generated builds. Add third-party attribution when adapting code.

For bug reports, include expected behavior, the shortest reproduction, browser
version, field type, and whether it happens in the playground or installed extension.
