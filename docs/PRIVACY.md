# Privacy and permissions

The Chrome extension operates on explicit shortcuts in supported input fields.
It reads the text around the caret to apply an exact matching shortcut. Text and
the one-step undo state remain in page memory; no typing-history log is stored.
There is no analytics service, remote model, or network API in the extension.

Saved profile names, shortcut patterns, replacements, active profile, and the
enabled/paused flag use `chrome.storage.sync`. Chrome may synchronize those
settings across the browsers signed into your account. Do not put passwords or
other confidential material in shortcut replacements.

The manifest requests:

- **storage**, to save and synchronize settings;
- static content-script matching for **HTTP and HTTPS pages**, so shortcuts can
  work in ordinary text fields. Chrome may show a warning about access to website
  content. You can restrict the extension's site access in Chrome.

It does not request browsing history, clipboard access, tabs, or remote code.
The extension skips password and unsupported input types, read-only/disabled
fields, marked credential/payment autocomplete fields, rich-text editors, and
elements inside `data-chordscribe="off"`. It does not run in iframes in this release.
These exclusions are not a promise to identify every sensitive field on every site.

On upgrade, saved profiles and the paused/enabled state are preserved, and any old
`typingHistory` key is removed. On uninstall, Chrome controls removal of extension
storage.

The local playground uses browser local storage instead of Chrome APIs. Its
settings belong to the playground origin and are separate from extension settings.

Chrome reference: [storage API](https://developer.chrome.com/docs/extensions/reference/api/storage).
