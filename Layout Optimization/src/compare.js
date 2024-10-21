const Stats = require('./stats');
const Layout = require("./layout");
const Runner = require("./runner");
const { text, trigrams, docs, code } = require("./data");
const { QWERTY, Workman, Colemak, Dvorak } = require('./presets');

const data = text;
const runner = new Runner(data, { effortLimit: 40000000 });
// const symbols = ['<','\\[','\\{','`','~','\!','@','\$','%','\\^','&','\\*','\\(','-','_','\\+','\\=','\\|', '\\\\','\\/'];
// const entries = symbols.map(symbol => (
//   [symbol, data.match(new RegExp(symbol, "g")).length]
// ));
// entries.sort((a, b) => a[1] > b[1] ? -1 : a[1] < b[1] ? 1 : 0);
// console.log(entries.map(e => `${e[0]} - ${e[1]}`).join('\n'));
// process.exit(0);


const Halmak1 = new Layout("Halmak1", `
\` 1 2 3 4 5 6 7 8 9 0 - =
 ~ ! @ # $ % ^ & * ( ) _ +
  f l r w k q p u d ; [ ] \\
  F L R W K Q P U D : { } |
  h s n t m y a e o i ' \\n
  H S N T M Y A E O I " \\n
  z x c v j g b , . /
  Z X C V J G B < > ?
`);

const Halmak2 = new Layout("Halmak2", `
\` 1 2 3 4 5 6 7 8 9 0 - =
 ~ ! @ # $ % ^ & * < > _ +
   v l r p z ; g u d q [ ] \\
   V L R P Z : G U D Q { } |
   h s n t , . a e o i ' \\n
   H S N T ( ) A E O I " \\n
   m f c w ? k y x b j
   M F C W / K Y X B J
`);

const Halmak21 = new Layout("Halmak21", `
\` 1 2 3 4 5 6 7 8 9 0 - =
 ~ ! @ # $ % ^ & * < > _ +
  c l r b z ; q u d j [ ] \\
  C L R B Z : Q U D J { } |
  s h n t , . a e o i ' \\n
  S H N T ( ) A E O I " \\n
  f m v w ? y g x k p
  F M V W / Y G X K P
`);

const Halmak22 = new Layout("Halmak22", `
\` 1 2 3 4 5 6 7 8 9 0 - =
 ~ ! @ # $ % ^ & * < > _ +
 w l r b z ; q u d j [ ] \\
 W L R B Z : Q U D J { } |
 s h n t , . a e o i ' \\n
 S H N T ( ) A E O I " \\n
 f m v c ? g p x k y
 F M V C / G P X K Y
`);



const LAYOUTS = [
  QWERTY, Workman, Colemak, Dvorak, Halmak1, Halmak2, Halmak21, Halmak22
];

console.log("Running measurements...");
const results = LAYOUTS.map(layout => {
  process.stdout.write(`  * ${layout.name} ... `);
  const result = runner.typeWith(layout);
  console.log("DONE");
  return { layout, stats: new Stats(result) };
});

console.log("\nRunning comparisons...\n");
const sorted = results.sort((a, b) => a.stats.position < b.stats.position ? -1 : 1);

sorted.forEach(result => {
  const { layout, stats } = result;
  const easineess = (stats.effort/stats.position).toFixed(2);
  const shortness = (stats.distance/stats.position).toFixed(3);
  const { data: { overheads: { sameFinger, sameHand, shifting} } } = stats;
  const overheads = {
    finger: sameFinger / stats.effort * 100 | 0,
    hand: sameHand / stats.effort * 100 | 0,
    shift: shifting / stats.effort * 100 | 0
  };

  console.log(layout.name, 'reached to:', stats.position, ', effort/symbol:', easineess, ', distance/symbol:', shortness, "\n");
  console.log(layout.toString());
  console.log(stats.fingersUsage.join(" "), ', ', stats.handsUsage.join(" | "));
  console.log("Symmetry:", stats.symmetry, "Evenness:", stats.evenness);
  console.log(`Overheads: F:${overheads.finger}%, H:${overheads.hand}%, S:${overheads.shift}%`);
  console.log("\n\n");
});
