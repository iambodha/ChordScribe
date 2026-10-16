# Research notes

## Real participant testing

ChordScribe was developed by Vibbodh Somani, Yamahn Tanjour, and Sarah Ali for
a Jugend forscht research project, documented in the German write-up
*Erstellen von effizienteren Tastaturen mit genetischen Algorithmen und Akkorden*.

The team carried out actual typing tests with **15 participants**. The write-up
reports:

| Measure | Reported result |
|---|---|
| Mean improvement | 18% |
| Median improvement | 12% |
| Participants with a positive result | 13 of 15 |
| Participants with a negative result | 2 of 15 |
| Range of percentage improvements | 62 percentage points |

Participants copied a supplied passage normally, then copied the same passage
using the provided shortcuts. Passages covered general, medical, legal, or
technical language. Both attempts were timed; optional feedback followed.

These are reported outcomes of real participant testing. The anonymized
participant-level timings, original test website, and original report are not
included in this repository, so the study statistics cannot yet be recomputed
from a fresh checkout. The current benchmark command evaluates the layout model;
it does not reproduce the participant experiment.

## Interpreting the result

The 18% figure is the team's mean improvement for that test and participant group.
It is not a guarantee for every user or task. The small sample, reuse of the same
passage, fixed normal-then-shortcuts order, and short familiarization period limit
generalization. The study also recorded negative results, which should remain
visible alongside the mean.

A future replication should retain anonymized timings with consent, define the
percentage-improvement formula, record errors as well as time, alternate test
order, use matched unfamiliar passages, and measure practice over multiple sessions.

## Layout simulation is a separate evaluation

The layout engine assigns estimated movement and effort costs to physical keys,
then applies same-finger and same-hand overheads while cycling through a corpus
until an effort budget is reached. The genetic search seeks layouts that advance
further within that budget.

Its scores depend on the selected corpus, fixed key mappings and penalties.
They do not measure learning time, physical comfort, fatigue, or human WPM.
The bundled corpus is a small smoke-test fixture, not a representative language
sample. See [the reproducible benchmark](BENCHMARK.md).
