# Reproducible layout benchmark

Run from the repository root with Node.js 24 or newer:

```bash
node scripts/benchmark.cjs --json
```

Input: `examples/corpus.txt`, 1522 characters. SHA-256:

```text
873b14bad0c00afdd5408fdfd16ea15c3df44c25108a1f93ea3af2c73fb9de69
```

Effort budget: 100,000 model units. The runner cycles the trimmed corpus until
that budget is reached, including the final key's effort. Lower per-character
costs are better within this model.

| Layout | Effort / character visited | Distance / character visited |
|---|---:|---:|
| QWERTY | 7.129 | 7.375 |
| Dvorak | 4.844 | 4.586 |
| Colemak | 3.943 | 4.115 |
| Workman | 3.737 | 4.356 |

Exact machine-readable results are in [benchmark.json](benchmark.json).
This tiny fixture checks that a clean checkout runs consistently; it does not
establish the best layout for English, German, or programming.

The legacy model uses physical key costs and hand/finger penalties. It skips
unsupported characters, while its position counter includes them. Distance uses
the source mapping's normalized units (tenths of a key size); it is not a measured
finger path. Shift overhead remains the legacy heuristic, not a complete
biomechanical model. Compare results only with the same corpus and configuration.

For a different corpus:

```bash
node scripts/benchmark.cjs --corpus /absolute/path/to/corpus.txt --effort 100000 --json
```

A custom corpus directory loads only its immediate `.txt` and `.md` files in
sorted order. No files are downloaded, and installed dependencies are not scanned.
The simulation result is separate from the [real participant shortcut study](RESEARCH.md).
