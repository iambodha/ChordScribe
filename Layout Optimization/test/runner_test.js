// Fixtures match the unchanged runner at main@99f722d; the old snapshots were stale.
const Runner = require('../src/runner');
const Layout = require('../src/layout');
const { QWERTY, Dvorak, Colemak, Workman } = require('../src/presets');
const text = global.TEXT_FIXTUE;

describe('Runner', () => {
  const runner = new Runner(text, {
    effortLimit: 2000,
    sameHandPenalty: 0.5,
    sameFingerPenalty: 5
  });

  it('counts stuff in QWERTY', () => {
    const result = runner.typeWith(QWERTY);
    delete(result.counts);
    expect(result).to.eql({
      distance: 2968,
      effort: 2003,
      overheads: {
        sameFinger: 370,
        sameHand: 277,
        shifting: 25
      },
      position: 395
    });
  });

  it('counts stuff in Dvorak', () => {
    const result = runner.typeWith(Dvorak);
    delete(result.counts);
    expect(result).to.eql({
      distance: 2486,
      effort: 2020,
      overheads: {
        sameFinger: 570,
        sameHand: 137,
        shifting: 43
      },
      position: 569
    });
  });

  it('counts stuff in Colemak', () => {
    const result = runner.typeWith(Colemak);
    delete(result.counts);
    expect(result).to.eql({
      distance: 2698,
      effort: 2004,
      overheads: {
        sameFinger: 35,
        sameHand: 374,
        shifting: 38
      },
      position: 725
    });
  });

  it('counts stuff in Workman', () => {
    const result = runner.typeWith(Workman);
    delete(result.counts);
    expect(result).to.eql({
      distance: 3053,
      effort: 2001,
      overheads: {
        sameFinger: 325,
        sameHand: 278,
        shifting: 56
      },
      position: 753
    });
  });
});
