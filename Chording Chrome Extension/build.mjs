import { build } from 'esbuild';
import { cp, mkdir, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.dirname(fileURLToPath(import.meta.url));
const outdir = path.join(root, 'dist');
await rm(outdir, { recursive: true, force: true });
await mkdir(outdir, { recursive: true });
await build({
  absWorkingDir: root,
  entryPoints: { background: 'background/index.ts', content: 'content/index.ts',
    'popup/index': 'popup/index.tsx', 'options/index': 'options/index.tsx' },
  outdir, bundle: true, format: 'iife', target: 'chrome120', jsx: 'automatic',
  define: { 'process.env.NODE_ENV': '"production"' }, minify: true, legalComments: 'linked',
});
await cp(path.join(root, 'manifest.json'), path.join(outdir, 'manifest.json'));
await cp(path.join(root, '..', 'LICENSE'), path.join(outdir, 'LICENSE'));
await cp(path.join(root, '..', 'THIRD_PARTY_NOTICES.md'), path.join(outdir, 'THIRD_PARTY_NOTICES.md'));
for (const page of ['popup', 'options']) {
  await cp(path.join(root, page, page + '.html'), path.join(outdir, page, page + '.html'));
}
console.log('Built ChordScribe in Chording Chrome Extension/dist');
