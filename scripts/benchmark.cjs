#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { parseArgs } = require('node:util');
const Runner = require('../Layout Optimization/src/runner');
const { QWERTY, Dvorak, Colemak, Workman } = require('../Layout Optimization/src/presets');
const { readCorpus } = require('../Layout Optimization/src/data');

function main() {
  const { values } = parseArgs({ options: {
    corpus: { type: 'string' }, effort: { type: 'string', default: '100000' },
    json: { type: 'boolean', default: false },
  } });
  const effortLimit = Number(values.effort);
  const corpusPath = path.resolve(values.corpus || process.env.CHORDSCRIBE_CORPUS ||
    path.join(__dirname, '../examples/corpus.txt'));
  const corpus = readCorpus(corpusPath);
  const runner = new Runner(corpus, { effortLimit });
  const results = [QWERTY, Dvorak, Colemak, Workman].map(layout => {
    const run = runner.typeWith(layout);
    return {
      layout: layout.name, charactersVisited: run.position,
      effort: run.effort, distance: run.distance,
      effortPerCharacter: run.effort / run.position,
      distancePerCharacter: run.distance / run.position,
    };
  });
  const report = {
    model: 'ChordScribe legacy effort model; not human WPM or an ergonomic validation',
    corpus: { path: path.relative(path.join(__dirname, '..'), corpusPath).split(path.sep).join('/'),
      sha256: createHash('sha256').update(corpus).digest('hex'), characters: corpus.length },
    effortLimit, results,
  };
  if (values.json) console.log(JSON.stringify(report, null, 2));
  else {
    console.log(report.model);
    console.log('Corpus SHA-256: ' + report.corpus.sha256);
    console.table(results.map(r => ({ layout: r.layout,
      'effort / character': r.effortPerCharacter.toFixed(3),
      'distance / character': r.distancePerCharacter.toFixed(3) })));
  }
}
try { main(); }
catch (error) { console.error('Benchmark failed: ' + error.message); process.exitCode = 1; }
