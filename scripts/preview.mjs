import { build } from 'esbuild';
import { createServer } from 'node:http';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outdir = path.join(root, '.preview');
await mkdir(outdir, { recursive: true });
await build({
  absWorkingDir: root,
  entryPoints: { options: 'Chording Chrome Extension/options/index.tsx',
    popup: 'Chording Chrome Extension/popup/index.tsx' },
  outdir, bundle: true, format: 'iife', jsx: 'automatic', target: 'chrome120',
  define: { 'process.env.NODE_ENV': '"development"' },
});
const shim = `
import { defaults, normalizeSettings, applyCommand } from "./Chording Chrome Extension/shared/settings.ts";
import { attachTypingSystem } from "./Chording Chrome Extension/content/controller.ts";
const listeners = new Set();
const key = "chordscribe-preview";
function read() {
  try { return normalizeSettings(JSON.parse(localStorage.getItem(key) || "null") || defaults()); }
  catch { return defaults(); }
}
let current = read();
function notify() { for (const listener of listeners) listener({}, "sync"); }
window.addEventListener("storage", event => {
  if (event.key === key) { current = read(); notify(); }
});
window.chrome = {
  storage: { sync: { get: async () => structuredClone(current) },
    onChanged: { addListener: listener => listeners.add(listener),
      removeListener: listener => listeners.delete(listener) } },
  runtime: { sendMessage: async command => {
    try {
      current = applyCommand(read(), command);
      localStorage.setItem(key, JSON.stringify(current)); notify();
      return { success: true, settings: structuredClone(current) };
    } catch (error) { return { success: false, error: error.message }; }
  }, openOptionsPage: async () => { location.href = "/options"; } },
};
attachTypingSystem(document, () => current);
`;
await build({ stdin: { contents: shim, resolveDir: root, loader: 'ts' },
  outfile: path.join(outdir, 'shim.js'), bundle: true, format: 'iife', target: 'chrome120' });

const page = (title, body, script = '') => `<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title></head><body>${body}<script src="/shim.js"></script>
${script ? '<script src="/' + script + '.js"></script>' : ''}</body></html>`;
const demo = page('ChordScribe playground', `<style>
body{font:16px/1.6 system-ui,sans-serif;color:#19232e;background:#fafbfc;margin:0}
main{max-width:720px;margin:64px auto;padding:0 24px}h1{font-size:36px;line-height:1.2}
a{color:#12549a;text-underline-offset:3px}nav{display:flex;gap:24px;margin:24px 0}
label{display:block;font-weight:600;margin:32px 0 8px}
textarea,input{box-sizing:border-box;width:100%;font:inherit;padding:12px;border:1px solid #8b98a5;border-radius:6px;background:#fff}
textarea{min-height:140px;resize:vertical}:focus-visible{outline:2px solid #12549a;outline-offset:3px}
p{max-width:65ch}code{background:#eaf1f8;padding:2px 5px;border-radius:3px}
</style><main><h1>Try your shortcuts.</h1>
<p>This local playground uses the extension's real expansion and settings logic.
Chrome APIs are simulated here; install the extension to verify browser integration.</p>
<nav><a href="/options">Manage shortcuts</a><a href="/popup">Open popup preview</a></nav>
<label for="writing">Writing area</label><textarea id="writing" placeholder="Type ty, then a space."></textarea>
<p>The default profile expands <code>ty</code> to <code>thank you</code> and <code>pls</code> to <code>please</code>.
Press Backspace immediately after an expansion to undo it. Settings persist only in this browser's local storage.</p>
<label for="protected">Opt-out field</label><input id="protected" type="text" data-chordscribe="off" placeholder="Shortcuts stay literal here.">
</main>`);
const pages = new Map([
  ['/', demo],
  ['/options', page('ChordScribe settings preview', '<div id="root"></div>', 'options')],
  ['/popup', page('ChordScribe popup preview', '<div id="root"></div>', 'popup')],
]);
const server = createServer(async (request, response) => {
  try {
    const pathname = new URL(request.url, 'http://localhost').pathname;
    if (pages.has(pathname)) {
      response.setHeader('Content-Type', 'text/html; charset=utf-8');
      response.end(pages.get(pathname)); return;
    }
    if (!['/shim.js', '/options.js', '/popup.js'].includes(pathname)) {
      response.writeHead(404); response.end('Not found'); return;
    }
    response.setHeader('Content-Type', 'text/javascript; charset=utf-8');
    response.end(await readFile(path.join(outdir, pathname.slice(1))));
  } catch { response.writeHead(500); response.end('Could not serve the preview.'); }
});
server.listen(4173, '127.0.0.1', () => console.log('ChordScribe preview: http://127.0.0.1:4173'));
server.on('error', error => { console.error('Could not start preview: ' + error.message); process.exitCode = 1; });
