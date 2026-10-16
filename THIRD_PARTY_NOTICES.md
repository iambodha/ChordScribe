# Third-party notices

## Keyboard Genetics

The inherited layout engine under `Layout Optimization/` and duplicated metric
utilities under `Chording/Fitness/` derive from Nikolay Nemshilov's
[Keyboard Genetics](https://github.com/kaievns/keyboard-genetics)
(previously MadRabbit/keyboard-genetics). The upstream `src/config.js` and
`src/runner.js` match the original project baseline; the genetic/layout/test
structure is inherited as well. ChordScribe adapts this foundation rather than
claiming authorship of the original engine. The effort-map source also references
[keyboard-analytics](https://github.com/MadRabbit/keyboard-analytics).

Upstream identifies its code as MIT licensed with the following copyright notice.
The MIT terms are reproduced below for the adapted code:

MIT License

Copyright (C) 2016 Nikolay Nemshilov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Bundled extension dependencies

React, Material UI, Emotion, and their dependencies retain their own notices.
The production build preserves bundled legal comments in the generated
`*.LEGAL.txt` files. Keep those files with the extension when distributing it.
The root lockfile records the installed dependency versions.
