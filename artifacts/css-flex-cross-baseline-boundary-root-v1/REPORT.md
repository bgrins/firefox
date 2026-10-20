# Flex baseline cross-size arithmetic boundary

Reviewing the collapsed-flex F12 operation ledger exposed a separate preexisting cross-size overflow. No collapsed children are needed.

For L=1073741823, two same-group items have outer sizes L and baseline distances -L,+L. Each provider and each outer-minus-start subtraction fits signed32, but independently selected start/end maxima sum to 3L. Four Lean results check this witness, a smaller control, and a sufficient component bound. The complete extracted `FlexLine::ComputeCrossSizeAndBaseline` body trips UBSan at the final addition under both O0 and O2 for first and last sharing groups; smaller values and auto-margin exclusion pass. The synthetic providers remain explicit. Completed native executables were removed.

A browser probe uses two ordinary items with equal heights and opposing positive/negative vertical margins. Installed Firefox158 and the shared Firefox160 build produce identical 27 rows with stable binary/source pins. In the calibrated v3 fixture, `max-height:100px` gives a representable expected final height. Six cases at 12M/14M/17M px with baseline or last-baseline alignment instead produce zero. All21 smaller-value/flex-start controls produce100px. Computed heights and margins retain the intended inputs. Huge physical item rectangles are separately clipped by coordinate limits, so they are not used as exact-size calibration.

The earlier v2 probe intentionally lacked max-height. Six mismatches there reflect ordinary range clamping; only the six zero-height results motivated the bounded v3 oracle. Its raw `matched` fields are diagnostic comparisons to unbounded arithmetic and are not all bug assertions. The first probe attempt ran before a body existed and yielded no observations; its logs and original source are retained as development evidence.

The current [Flexbox cross-size algorithm](https://drafts.csswg.org/css-flexbox-1/#cross-sizing) combines the two baseline-edge maxima and then clamps a single line to the container’s min/max cross sizes. This yields100px for v3. The indexed implementation retains the same addition. This evidence establishes a layout defect at extreme numeric inputs, not memory corruption or arbitrary data disclosure.

The separate native/WPT candidate is in `../css-flex-cross-baseline-overflow-fix-v1/`. It does not change the accepted or committed fix count until its review gates pass. Discovery order: formal operation-ledger review, kernel arithmetic witness, extracted-native UBSan, browser confirmation, then repair.
