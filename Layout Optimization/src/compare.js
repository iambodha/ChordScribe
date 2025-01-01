const Stats = require("./stats");
const Layout = require("./layout");
const Runner = require("./runner");
const fs = require("fs");
const path = require("path");
const { QWERTY, QWERTZ, Workman, Colemak, Dvorak } = require("./presets");

// Load both English and German text
const englishText = fs.readFileSync(
  path.join(__dirname, "../text/englishText.txt"),
  "utf8"
);
const germanText = fs.readFileSync(
  path.join(__dirname, "../text/germanText.txt"),
  "utf8"
);

console.log("Running measurements with English text...");
const englishRunner = new Runner(englishText, { effortLimit: 40000000 });
const englishResults = [QWERTY, Workman, Colemak, Dvorak].map((layout) => {
  process.stdout.write(`  * ${layout.name} (English) ... `);
  const result = englishRunner.typeWith(layout);
  console.log("DONE");
  return { layout, stats: new Stats(result) };
});

console.log("\nRunning measurements with German text...");
const germanRunner = new Runner(germanText, { effortLimit: 40000000 });
const germanResults = [QWERTZ, QWERTY].map((layout) => {
  process.stdout.write(`  * ${layout.name} (German) ... `);
  const result = germanRunner.typeWith(layout);
  console.log("DONE");
  return { layout, stats: new Stats(result) };
});

// Combine results
const allResults = [...englishResults, ...germanResults];

console.log("\nRunning comparisons...\n");
const sorted = allResults.sort((a, b) =>
  a.stats.position < b.stats.position ? -1 : 1
);

sorted.forEach((result) => {
  const { layout, stats } = result;
  const easiness = (stats.effort / stats.position).toFixed(2);
  const shortness = (stats.distance / stats.position).toFixed(3);
  const {
    data: {
      overheads: { sameFinger, sameHand, shifting },
    },
  } = stats;
  const overheads = {
    finger: ((sameFinger / stats.effort) * 100) | 0,
    hand: ((sameHand / stats.effort) * 100) | 0,
    shift: ((shifting / stats.effort) * 100) | 0,
  };

  console.log(
    layout.name,
    "reached to:",
    stats.position,
    ", effort/symbol:",
    easiness,
    ", distance/symbol:",
    shortness,
    "\n"
  );
  console.log(layout.toString());
  console.log(stats.fingersUsage.join(" "), ", ", stats.handsUsage.join(" | "));
  console.log("Symmetry:", stats.symmetry, "Evenness:", stats.evenness);
  console.log(
    `Overheads: F:${overheads.finger}%, H:${overheads.hand}%, S:${overheads.shift}%`
  );
  console.log("\n\n");
});
