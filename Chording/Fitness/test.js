const { Halmak } = require('./presets');
const { analyzeWord } = require('./word-analysis');

const stats = analyzeWord(Halmak, "hello");
console.log({
  effort: stats.effort,
  distance: stats.distance,
  fingersUsage: stats.fingersUsage,
  handsUsage: stats.handsUsage,
  rowsUsage: stats.rowsUsage,
  symmetry: stats.symmetry,
  evenness: stats.evenness
});