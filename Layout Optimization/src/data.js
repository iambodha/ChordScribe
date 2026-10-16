const fs = require('node:fs');
const path = require('node:path');
const SAMPLE = path.resolve(__dirname, '../../examples/corpus.txt');

function readCorpus(source = process.env.CHORDSCRIBE_CORPUS || SAMPLE) {
  const resolved = path.resolve(source);
  if (!fs.existsSync(resolved)) throw new Error('Corpus not found: ' + resolved);
  const info = fs.statSync(resolved);
  if (info.isFile()) return fs.readFileSync(resolved, 'utf8');
  if (!info.isDirectory()) throw new Error('Corpus must be a file or directory.');
  const files = fs.readdirSync(resolved, { withFileTypes: true })
    .filter(entry => entry.isFile() && /\.(txt|md)$/i.test(entry.name))
    .map(entry => entry.name).sort();
  if (!files.length) throw new Error('Corpus directory has no .txt or .md files: ' + resolved);
  return files.map(name => fs.readFileSync(path.join(resolved, name), 'utf8')).join('\n\n');
}

exports.readCorpus = readCorpus;
// Lazy reads keep module imports independent of a local private dataset.
Object.defineProperty(exports, 'text', { get: () => readCorpus() });
Object.defineProperty(exports, 'docs', { get: () => fs.readFileSync(path.resolve(__dirname, '../../README.md'), 'utf8') });
Object.defineProperty(exports, 'code', { get: () => fs.readFileSync(path.join(__dirname, 'runner.js'), 'utf8') });
exports.trigrams = 'the and ing her hat his tha ere for ent ion ter was you ith ver all wit thi tio';
exports.bigrams = 'th he in er an re nd on en at ou ed ha to or at is it hi es ng';
