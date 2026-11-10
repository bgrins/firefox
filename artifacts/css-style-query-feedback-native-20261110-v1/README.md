# First native feedback trace

The diagnostic build and four-mode WPT completed successfully: 4 PASS / 1 OK.
The raw log contains 4,452 output rows with native trace text and no cap record. However, four lines
contain interleaved output from different browser processes. `LOG-INTEGRITY.json`
retains the exact lines and the raw-log hash. This run cannot support an
exhaustive claim about event absence or balanced complete traces.

The diagnostic logger wrote each record using several stdio calls. Separate
processes sharing the output stream could splice those calls together. A second
diagnostic will construct a complete bounded record before a single OS write.
The fixture and native behavior under investigation stay the same.

Intact early opposed and aligned intervals show readiness at style depth zero,
followed by two association changes within later returning style calls. These
local observations explain how repeated JS snapshots can be pending despite
intervening readiness. They do not establish global convergence, an infinite
loop, a performance impact, or a new production defect. The final interpretation
depends on the corrected complete trace.

`ROOT-RESTORATION.json` independently verifies all four native sources, the full
application bundle and extras, the current build's binary hashes, unchanged
HEAD/index, absence of owned build/browser process groups, and removal of the
temporary fixture and backup. The current testing build is restored.

The source patch and independent review are retained in the adjacent
`css-style-query-feedback-instrumentation-20261110-v1` and
`css-style-query-feedback-instrumentation-review-20261110-v1` capsules. This is
diagnostic research only; repair #160 remains held and no repair is counted.
