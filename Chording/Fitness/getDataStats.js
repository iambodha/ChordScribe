const { Halmak } = require('./presets');
const { analyzeWord } = require('./word-analysis');
const fs = require('fs');

// Load the dataset
const tokens = JSON.parse(fs.readFileSync('../filtered_token_frequencies.json', 'utf-8'));

// Helper function to compute min, max, mean, and std deviation
function calculateStats(array) {
    let min = Infinity;
    let max = -Infinity;
    let sum = 0;
    let sumOfSquares = 0;

    for (const val of array) {
        if (val < min) min = val;
        if (val > max) max = val;
        sum += val;
        sumOfSquares += val ** 2;
    }

    const mean = sum / array.length;
    const variance = sumOfSquares / array.length - mean ** 2;
    const stdDev = Math.sqrt(variance);

    return { min, max, mean, stdDev };
}

// Initialize arrays to collect data
let effort = [], distance = [], symmetry = [], evenness = [];
let fingersUsage = [], handsUsage = [], rowsUsage = [];

// Helper function to process a batch of tokens
function processBatch(batch) {
    for (const word in batch) {
        const stats = analyzeWord(Halmak, word);
        effort.push(stats.effort);
        distance.push(stats.distance);
        symmetry.push(stats.symmetry);
        evenness.push(stats.evenness);

        fingersUsage.push(...stats.fingersUsage);
        handsUsage.push(...stats.handsUsage);
        rowsUsage.push(...stats.rowsUsage);
    }
}

// Process tokens in batches
const batchSize = 1000; // Adjust batch size as needed
let batch = {};
let count = 0;

for (const word in tokens) {
    batch[word] = tokens[word];
    count++;
    if (count >= batchSize) {
        processBatch(batch);
        batch = {};
        count = 0;
    }
}

// Process remaining tokens
if (count > 0) {
    processBatch(batch);
}

// Calculate stats for each metric
const effortStats = calculateStats(effort);
const distanceStats = calculateStats(distance);
const symmetryStats = calculateStats(symmetry);
const evennessStats = calculateStats(evenness);

const fingersStats = calculateStats(fingersUsage);
const handsStats = calculateStats(handsUsage);
const rowsStats = calculateStats(rowsUsage);

// Output the results
console.log({
    effortStats,
    distanceStats,
    symmetryStats,
    evennessStats,
    fingersStats,
    handsStats,
    rowsStats
});
