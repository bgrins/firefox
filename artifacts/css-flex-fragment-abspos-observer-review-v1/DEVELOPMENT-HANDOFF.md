# Executable proposal handoff

These are unrun proposals, not landed or browser-validated tests. Root owns browser execution and copied the original relative proposal before its paired run; do not mutate those retained bytes.

## Relative offsets

`relative-offset-wpt.html` loads `relative-offset-probe.js` and WPT testharness resources. Copy both to the same served WPT directory, or adjust only the script URL in the wrapper. Defaults: 432 configurations × three separate observations = 1296 subtests. Items, flow-fragment/marker geometry and restoration are separate. The independent absolute-position reference allows the same CSSOM rounding as the tested writing mode without allowing the candidate an extra tolerance.

For standalone browser collection, serve `relative-offset-probe.html` and evaluate `collectRelativeOffsetRows(options)`. Options replace the default arrays; e.g. `{writingModes:["vertical-rl"], offsets:[[11,17],[-11,-17]], heights:[160,16000000], counts:[4]}`. Raw rows include independent calibration, all actual/expected rectangles and restoration. Do not treat baseline flow failures as item failures.

## Absolute continuations

Serve `abspos-continuation-probe.html`, then `collectAbsposContinuationRows(options)`. Defaults216 rows. Suggested first pass: `{blockOffsets:[0], counts:[4,8]}` gives48 rows. Single-child controls and a block with tiny forced-break descendants share a positioned flex containing block. Span children target abspos continuation handling and the separate cumulative containing-block field. Explicit insets remove hypothetical static-position ambiguity from this first experiment.

`absoluteItemGeometry` and `absoluteContinuationCount` are diagnostic predictions requiring calibration against small cases and current fragmentation policy before promotion to a WPT oracle. They are not asserted normative results merely because CSS.supports accepts the break syntax. `itemSizesCalibrated`, numeric/reference calibration, computed break values and restoration are separate raw fields.

## True overflow continuation candidate

Serve `overflow-container-probe.html`, then `collectOverflowContainerRows(options)`. Defaults16 rows. A fixed80px first flex item contains tiny20px descendants with forced breaks; other80px flex items also force column breaks. This aims to create true overflow continuations of the fixed-size item beside ordinary line items. Confirm the branch using actual fragment shapes or logging before claiming source reachability. Small160px controls precede16m cases. Per-item fragment arrays are retained because a bounding rectangle of a fragmented item is not a single-fragment geometry oracle.

All collectors remove fixtures in finally blocks and retain numeric rows only. No browser, native-source, Git or build mutation is performed by these files themselves beyond ordinary in-page DOM layout.
