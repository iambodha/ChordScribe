const { QWERTZ } = require('./presets');
const { analyzeWord } = require('./word-analysis');
const normalization = require('./normalization');
const fs = require('fs');

// Load the dataset
const tokens = JSON.parse(fs.readFileSync('./tokens.json', 'utf-8'));

// Normalize a metric
function normalize(value, { min, max }) {
    return (value - min) / (max - min);
}

// Scoring weights
const weights = {
    effort: 0.3,
    distance: 0.3,
    fingers: 0.2,
    hands: 0.1,
    rows: 0.1
};

// Helper function for variance calculation
function variance(array) {
    const mean = array.reduce((sum, x) => sum + x, 0) / array.length;
    return array.reduce((sum, x) => sum + (x - mean) ** 2, 0) / array.length;
}

// Function to calculate score
function calculateScore(stats, frequency) {
    const effort = normalize(stats.effort, normalization.effort);
    const distance = normalize(stats.distance, normalization.distance);
    const fingersImbalance = normalize(variance(stats.fingersUsage), normalization.fingers);
    const handsImbalance = normalize(Math.abs(50 - stats.handsUsage[0]), normalization.hands);
    const rowsImbalance = normalize(variance(stats.rowsUsage), normalization.rows);

    const weightedScore = (
        weights.effort * effort +
        weights.distance * distance +
        weights.fingers * fingersImbalance +
        weights.hands * handsImbalance +
        weights.rows * rowsImbalance
    );

    return frequency * weightedScore; // Higher score for higher effort/strain
}

// Add scores to the tokens
const scoredTokens = {};
for (const word in tokens) {
    const stats = analyzeWord(QWERTZ, word);
    const frequency = tokens[word];
    const score = calculateScore(stats, frequency);

    scoredTokens[word] = {
        frequency,
        score
    };
}

// Save updated tokens to a new JSON file
fs.writeFileSync('./scored_tokens.json', JSON.stringify(scoredTokens, null, 2), 'utf-8');
console.log('Scores calculated and saved to scored_tokens.json');
