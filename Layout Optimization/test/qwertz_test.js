const Runner = require("../src/runner");
const { QWERTZ, QWERTY } = require("../src/presets");

describe("QWERTZ Layout with German Text", () => {
  const runner = new Runner(global.TEXT_FIXTURE_DE, {
    effortLimit: 2000,
    sameHandPenalty: 0.5,
    sameFingerPenalty: 5,
  });

  it("performs better than QWERTY for German text", () => {
    const qwertzResult = runner.typeWith(QWERTZ);
    const qwertyResult = runner.typeWith(QWERTY);

    // Remove counts for cleaner comparison
    delete qwertzResult.counts;
    delete qwertyResult.counts;

    // QWERTZ should have:
    // 1. Lower effort (more efficient for German)
    // 2. Lower distance (better positioned special characters)
    // 3. Lower same-finger and same-hand overheads
    expect(qwertzResult.effort).to.be.below(qwertyResult.effort);
    expect(qwertzResult.distance).to.be.below(qwertyResult.distance);
    expect(qwertzResult.overheads.sameFinger).to.be.below(
      qwertyResult.overheads.sameFinger
    );
    expect(qwertzResult.overheads.sameHand).to.be.below(
      qwertyResult.overheads.sameHand
    );

    console.log("\nQWERTZ Performance with German text:");
    console.log("Position reached:", qwertzResult.position);
    console.log("Total effort:", qwertzResult.effort);
    console.log("Total distance:", qwertzResult.distance);
    console.log("Overheads:", qwertzResult.overheads);

    console.log("\nQWERTY Performance with German text:");
    console.log("Position reached:", qwertyResult.position);
    console.log("Total effort:", qwertyResult.effort);
    console.log("Total distance:", qwertyResult.distance);
    console.log("Overheads:", qwertyResult.overheads);
  });
});
