const Runner = require('../src/runner');
const Population = require('../src/population');
const Cluster = require('../src/cluster');
const { QWERTY } = require('../src/presets');

describe('Input and worker lifecycle', () => {
  it('rejects missing and non-progressing corpora instead of hanging', () => {
    expect(() => new Runner('')).to.throw(/non-empty/);
    expect(() => new Runner('漢字').typeWith(QWERTY)).to.throw(/no effort/);
    expect(() => new Runner('sss').typeWith(QWERTY)).to.throw(/no effort/);
    expect(() => new Runner('hello', { effortLimit: Infinity }).typeWith(QWERTY)).to.throw(/finite/);
    expect(() => new Runner('hello', { effortLimit: 0 }).typeWith(QWERTY)).to.throw(/positive/);
  });
  it('initializes population scores', () => {
    const genome = {};
    expect(new Population([genome]).scoreFor(genome)).to.eql({ total: 0 });
  });
  it('isolates pools with different corpora and closes without leaking tasks', async () => {
    const first = new Cluster('hello world', { effortLimit: 2000 });
    const second = new Cluster('keyboard research', { effortLimit: 2000 });
    try {
      const [[one], [two]] = await Promise.all([
        Promise.all(first.schedule([QWERTY])), Promise.all(second.schedule([QWERTY])),
      ]);
      expect(one.result).to.eql(new Runner('hello world', { effortLimit: 2000 }).typeWith(QWERTY));
      expect(two.result).to.eql(new Runner('keyboard research', { effortLimit: 2000 }).typeWith(QWERTY));
    } finally { first.close(); second.close(); }
    expect(() => first.schedule([QWERTY])).to.throw(/closed/);
  });
  it('returns worker validation errors to the caller', async () => {
    const pool = new Cluster('漢字');
    try {
      let failure;
      try { await Promise.all(pool.schedule([QWERTY])); } catch (error) { failure = error; }
      expect(failure.message).to.match(/no effort/);
    } finally { pool.close(); }
  });
});
