# Random rollback at complete typed numeric parse boundaries

Recommendation: retain the registered whole-alternative transaction and add transactions around the complete `CalcNode::parse_number` and `parse_percentage` Result. The resulting proposal changes three native paths. It extends the same rollback family; it does not modify the sealed predecessor or claim another accepted bug.

## Placement comparison

| Placement | Advantages | Limits |
|---|---|---|
| Wrap NumberOrPercentage's Percentage attempt and LineHeight's Number attempt | Smallest direct correspondence to the two observed ordinary paths; token rollback is adjacent | Repeats the invariant per union; misses AngleOrPercentage and other callers of the same failed numeric type parse |
| Wrap complete CalcNode typed Number/Percentage parse | One boundary for each discarded typed result; includes both syntax failure and final type rejection; covers Number and Integer wrappers plus Percentage callers | Does not cover successful typed output later rejected by its caller, other typed finalizers, or every speculative parser |

The second placement is preferable for this family. `Self::parse` alone is insufficient: the decisive failure follows successful generic math parsing, in `into_number` or `into_percentage`. Both consume the owned CalcNode and return an owned CalcNumeric only on success. On Err there is no output parameter, callback receiving an AST, or retained parsed value. The failed tree is dropped. Random keys are constructed during parsing; context random-base lookup occurs when computing, not when these typed parsers return an error.

The helper snapshots the entry count and restores only on Err. If a prior successful member has already consumed k indexes, a failed nested parse restores k, not zero. Successful calls retain all increments, including nested random functions and functions later simplified away: the specification assigns indexes before canonicalization. Nested helper scopes compose: inner failure rolls back to its own entry; later outer failure rolls back the entire discarded outer attempt. No token rewind is added here—existing callers retain that responsibility. No generic ParserContext effect rollback or unwind-on-panic guarantee is introduced.

The registered whole-alternative transaction remains essential. A typed scalar can successfully parse one function, then `parse_entirely` rejects trailing tokens and retries a list alternative. A typed parser cannot detect that later failure. Original parser.rs and properties_and_values/value.rs proposal bodies are byte-identical to the predecessor; DELTA.patch contains only the two complete typed wrappers in calc.rs.

## Coverage and exclusions

This covers Percentage-first NumberOrPercentage (opacity, shared filter/border-image callers), Number-first LineHeight, and Percentage-first AngleOrPercentage. Number and Integer both call CalcNode::parse_number. It may help shorthand retries that fail through those entry points, but it is not a proof that all shorthand parser state is restored. Failed Length, LengthPercentage, Angle, Time or Resolution parses are not newly wrapped. A successful typed parse later rejected by a range/grammar/caller is outside this inner boundary unless an enclosing transaction handles it. Do not present this as a global speculative-parser repair.

No root native mutation or browser execution was performed by this package. The same selected parser/type-rejection blocks occur in captured upstream and local sources; differing surrounding code is pinned in the ordinary audit. The three-path patch is based on exact branch captures, not a claim that all files transport unchanged to upstream.

## Runtime evidence remains separate

Root reports that the ordinary observer reproduces numeric opacity and length line-height using index2 rather than1, including explicit CSSOM key strings. Root also found the number line-height control computes0px for both compared indexed values. That computed equality is vacuous and must not be counted as a calibrated positive control. Its specified index1 remains useful, but should be paired with literal/fixed/named number calibration.

Source inspection gives a separate cause for the zero: `LineHeight::to_computed_value` uses `map_line_height_leaf`, which resolves only Length/Percentage and clones RandomKey. Ordinary CalcNumeric resolution converts a RandomKey through `Leaf::to_computed_value(Some(context))`. This is a distinct special-computation-path issue, not fixed or silently folded into this counter rollback proposal. Root owns further runtime attribution; no new fix count follows.

## Suggested validation

Keep the existing registered single/list/failed-list/trailing-token cases and the ordinary two source witnesses. Add the bounded cases in WPT-CONTROLS.json for preserved successful member counts, nonzero entry restoration, and nested function indexes. Expected comparisons use authored explicit ua keys and identical property/ranges, not different-key inequality. Percentage-first and fixed/named controls should pass independently. Treat ordinary number line-height computed value separately until its mapper issue is resolved; do not weaken its real expected result to0.

The conic-gradient control exercises an additional known caller, not another bug count. All newly suggested multi-function cases are unexecuted and require support/static/browser calibration before inclusion as landing gates.

## Validation

Exact three-path forward/reverse/reapply and rustfmt checks passed21c41e/0 in owned scratch; scratch removed. Bounded independent source review by counter_comparison_review cleared DELTA/owned-result/nested-count semantics (c78419/0,2a876c/0), with the limits above. No Rust typecheck or native/browser test has run for this proposal.
