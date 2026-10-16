import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = path.join(root, 'Chording Chrome Extension/dist');
const manifest = JSON.parse(await readFile(path.join(source, 'manifest.json'), 'utf8'));
const entries = [];
async function walk(directory, prefix = '') {
  for (const entry of (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name))) {
    const name = prefix + entry.name;
    if (entry.isDirectory()) await walk(path.join(directory, entry.name), name + '/');
    else entries.push({ name, data: await readFile(path.join(directory, entry.name)) });
  }
}
await walk(source);
// ZIP "store" entries: no platform-specific zip executable or extra dependency.
// Fixed timestamps and sorted paths make repeated builds byte-for-byte comparable.
function crc32(data) {
  let crc = 0xffffffff;
  for (const byte of data) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}
const local = [], central = [];
let offset = 0;
for (const { name, data } of entries) {
  const filename = Buffer.from(name);
  const header = Buffer.alloc(30);
  header.writeUInt32LE(0x04034b50);
  header.writeUInt16LE(20, 4); header.writeUInt16LE(0x800, 6);
  header.writeUInt16LE(33, 12);
  header.writeUInt32LE(crc32(data), 14);
  header.writeUInt32LE(data.length, 18); header.writeUInt32LE(data.length, 22);
  header.writeUInt16LE(filename.length, 26);
  local.push(header, filename, data);
  const record = Buffer.alloc(46);
  record.writeUInt32LE(0x02014b50);
  record.writeUInt16LE(20, 4); record.writeUInt16LE(20, 6); record.writeUInt16LE(0x800, 8);
  record.writeUInt16LE(33, 14);
  record.writeUInt32LE(crc32(data), 16);
  record.writeUInt32LE(data.length, 20); record.writeUInt32LE(data.length, 24);
  record.writeUInt16LE(filename.length, 28); record.writeUInt32LE(offset, 42);
  central.push(record, filename);
  offset += header.length + filename.length + data.length;
}
const directory = Buffer.concat(central);
const end = Buffer.alloc(22);
end.writeUInt32LE(0x06054b50);
end.writeUInt16LE(entries.length, 8); end.writeUInt16LE(entries.length, 10);
end.writeUInt32LE(directory.length, 12); end.writeUInt32LE(offset, 16);
const output = path.join(root, 'artifacts', 'chordscribe-extension-' + manifest.version + '.zip');
await mkdir(path.dirname(output), { recursive: true });
await writeFile(output, Buffer.concat([...local, directory, end]));
console.log('Packaged ' + path.relative(root, output));
