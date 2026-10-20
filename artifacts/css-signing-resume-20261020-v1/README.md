# Signed queue completion

101 native/WPT fixes are now committed locally. This batch adds 14 fixes and
34 preceding evidence/proof commits. No accepted fixes remain pending signing.
No pushes, submissions, or new runtime verification were performed by this step.

| Fix | Repair | Native + WPT commit | Preceding companion |
| --- | --- | --- | --- |
| 88 | view-transition-type-style-invalidation | `c67505af9aae8c06150d74d81a67011e7921d3cd` | `85ed2f301cf00df468f6d071c1322c9767e64bba` |
| 89 | sticky-explicit-inset-auto-alias | `fdd7dcb11653c3c3808557708969c7e1eb803b82` | `de1fa6e8539a1d7d08514cfde240f0f572a16046` |
| 90 | sticky-auto-inset-normalization | `983931aa5fad14b5d86120cfd66635be7f1b844f` | `402fc4d824b0a8064b1e124fb0d2de413bf64fac` |
| 91 | sticky-containing-block-writing-mode | `67bcf64fc28f181859c6dc726e532430475e49e7` | `05b8cda1a77cb28ce532c3bf3e40483b6dd8d212` |
| 92 | sticky-negative-inset-overflow | `d3c505adc9e99a293a44bde5a3f04557aac255d0` | `b0d56f61ff11561282f0bdf5500959ae1a79fdb9` |
| 93 | flex-baseline-cross-size-sum | `71a523a4c5267ba4c07a59329e57317fafc31f1b` | `edd86929946a555f4c8527577ee10d582efdf716` |
| 94 | sticky-finite-sentinel | `68686da757592b0de4d1b064966d81f8b9265fc1` | `8ce52f459152c455bfdde8ee74fc39d447e62cf8` |
| 95 | flex-line-cross-size-sum | `958e63a947e4a97dd224d60c5699b42061af5422` | `5c3d2e1ec59a4cdb940f40a837daf108189adef2` |
| 96 | flex-relative-item-exported-baseline | `b4894d6329df7b9cae8f81cbd72e89d61f1b4adc` | `2ba42b38c6557fcbda3ae8bcefdcdc1835c86c09` |
| 97 | scroll-container-natural-baseline-border-conversion | `9980b7b7a0fb894c963a69c0ef0e17b12e6d6350` | `2dc0fa3aa371a02d67ce129c3c394c1c82b81b03` |
| 98 | flex-baseline-percentage-padding-measurement-cache | `f5926c6dab500569fc2345aade1a43aebc7e3796` | `55ca79bc149d5ffc2773e3e0b0216bfe3dc8dbf8` |
| 99 | flex-vertical-rl-overflow-container-position | `a6c78d9502504d07432fd0c81c168847bbfa25a4` | `052dc13ae43ddb8a86edda92f70abba7ba9fdbe7` |
| 100 | overflow-continuation-relative-position | `2b769488eef1e2ae18ed27d014402591110e3ed1` | `dcdf5a89d3589bd31ad115988fd8af898b2c753b` |
| 101 | flex-table-auto-caption-percentage-height-cache | `6cf27eadddf9e63d9bfbcc87ff2bf354e091ae7c` | `4d0749e7d3c43516d8d265901d7c6a918c99f7fa` |

[Verification](ROOT-COMMIT-CHECK.json) checks signatures are present, exact file
rosters, parent relationships, and native patches applied and reversed against
the actual parents in disposable indexes. It does not re-run browser tests.

The six preexisting unaccepted repair candidates remain excluded. Two newer
investigations are also excluded: reached signed table arithmetic overflow and
a reduced CSSOM rectangle precision discrepancy. Neither has an accepted repair
or demonstrated security impact.
