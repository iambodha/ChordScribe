const Layout = require('./layout');
const Stats = require('./stats');

function analyzeWord(layout, word) {
  // Initialize counters
  const data = {
    effort: 0,
    distance: 0,
    position: 0,
    counts: {},
    overheads: {
      sameFingerOverhead: 0,
      handAlternationOverhead: 0,
      rowChangeOverhead: 0
    }
  };

  // Initialize finger counts matrix (8 fingers × 4 rows)
  'l-pinky l-ring l-middle l-point r-point r-middle r-ring r-pinky'.split(' ').forEach(finger => {
    data.counts[finger] = [0, 0, 0, 0];
  });

  // Get the metrics mapping for the layout
  const metrics = layout.toMetrics();
  let prevKey = null;

  // Analyze each character in the word
  for (let char of word) {
    const keyMetrics = metrics[char];
    if (!keyMetrics) continue; // Skip if character not found in layout

    // Add base metrics
    data.effort += keyMetrics.effort;
    data.distance += keyMetrics.distance;
    data.position += 1;

    // Track finger usage by row
    if (keyMetrics.finger !== 'thumb') {
      data.counts[keyMetrics.finger][keyMetrics.row] += 1;
    }

    // Calculate overheads if we have a previous key
    if (prevKey) {
      // Same finger overhead
      if (keyMetrics.finger === prevKey.finger && keyMetrics.finger !== 'thumb') {
        data.overheads.sameFingerOverhead += 1;
      }

      // Hand alternation overhead (penalty for same hand)
      if (keyMetrics.hand === prevKey.hand && keyMetrics.hand !== false) {
        data.overheads.handAlternationOverhead += 0.5;
      }

      // Row change overhead
      if (keyMetrics.row !== prevKey.row) {
        data.overheads.rowChangeOverhead += Math.abs(keyMetrics.row - prevKey.row) * 0.5;
      }
    }

    prevKey = keyMetrics;
  }

  return new Stats(data);
}

module.exports = { analyzeWord };
