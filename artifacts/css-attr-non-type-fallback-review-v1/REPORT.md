# Independent review: non-type attribute fallback cycles

Verdict: no concrete native correctness or API/lifetime blocker found in the sealed v1 proposal. Proceed with the original/candidate native and WPT validation. This is a source review, not an accepted bugfix or a claim that the code compiled or passed a browser. The reviewed proposal manifest is `1b26748fd78502430df8e191c1630046797917fc7b6fa5f1807f68eabdabadec`; all 24 listed payload hashes matched.

## Native review

`parse_attr_number` retains the original operation order: skip leading whitespace, record token start, accept exactly a number token, capture the original token spelling, then require exhaustion. The unit-producing substitution path still appends its unit after this shared operation and preserves the existing Number/Percentage/Dimension serialization tags and attr-tainted result. The new classifier does not manufacture substitution text or change taint propagation.

The current cssparser source declares `Parser<'i>`. Its `slice_from`, implemented on `Parser<'a>` in tokenizer.rs, returns `&'a str` from the input rather than borrowing the mutable parser. Consequently keeping that slice across `expect_exhausted` is valid at source/API level, and the temporary parser used with the owned attribute String cannot escape through `.is_ok()`. `expect_exhausted` ignores trailing whitespace/comments and resets its cursor; capturing the token slice first preserves the old behavior. This was inspected against fetched Searchfox sources, not tested with a native compiler.

The classifier uses the occurrence's parsed namespace and LocalName conversion through AttributeTracker, matching actual substitution. Unknown namespace or absent attribute fails; present raw/bare text, including empty text and literal function text, succeeds; number/unit syntax uses the same primitive as substitution. A typed-cache entry from another occurrence cannot decide this branch. The extra graph-time attribute query is important when a cycle removes the property before normal substitution: the attribute must still remain an invalidation dependency. It may duplicate a later successful substitution query; no performance measurement was done.

The new call occurs only inside the Attr branch, after `can_chain` is false and only if a fallback exists. In this branch `is_attr_with_type()` is false, so the helper's Type arm is unreachable by the actual caller. Used fallback references are pushed into the same SCC traversal, retaining cycle and non-custom dependency handling. Present raw and successfully parsed numeric primaries do not admit unused fallback edges. The parent-attribute exception remains unchanged: this patch does not fix or adjudicate the separate raw-string false cycle inside a typed attribute node.

## Existing WPT review and coverage finding

The 28 fixed cases and two mutation tests have consistent oracles. A used self/mutual cycle invalidates the unregistered custom participants and causes the consuming color's green fallback. Present raw values serialize as strings, including the empty string, and numeric/unit values do not satisfy the color grammar, so those controls inherit black. Namespace setup uses a stylesheet namespace rule and `setAttributeNS`, while parse assertions prevent an invalid declaration from silently passing via inheritance. The occurrence-specific raw/number case correctly distinguishes two syntaxes for the same attribute. Mutation cases cover missing to valid to empty to missing states and therefore exercise graph-time tracking when ordinary substitution is bypassed by invalidation.

Coverage finding addressed by the attached supplement: all original 30 cases place attr() in custom-property declarations, but the changed traversal branch also handles NonCustom roots. The existing `attr-noncustom-dependency-cycles.html` roster uses type() occurrences, so it does not cover this particular new branch. Four proposed cases now exercise font-size and line-height directly, including valid-primary controls.

## Four-case supplement and oracle derivation

`noncustom-supplement.js` and `supplement.patch` append four tests to the exact v1 WPT. `combined/testing/web-platform/tests/css/css-values/attr-non-type-used-fallback-cycle.html` is the resulting 34-test fixture, SHA-256 `6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3`. No existing v1 case or native body is changed. `SUPPLEMENT-PROVENANCE.json` pins the inputs and existing typed-cycle calibration.

The parent has font-size 23px and line-height 31px. The non-inherited registered length has initial value 11px. A missing or invalid numeric primary activates the fallback reference; combined with 1em or 1lh this makes the corresponding dependency cycle. The font-size/line-height declaration defaults to its inherited parent value and the registered property to 11px. A valid primary of 13 yields 13px without following the cyclic fallback; the registered relative length and width then compute to 13px. The line-height case uses invalid numeric text rather than merely a missing attribute and checks both font-size and line-height explicitly.

| Case | Registered length | Font size | Line height | Width |
| --- | --- | --- | --- | --- |
| Font size, missing px primary | 11px | 23px | 31px | 11px |
| Font size, valid 13 primary | 13px | 13px | 31px | 13px |
| Line height, invalid px primary | 11px | 23px | 31px | 11px |
| Line height, valid 13 primary | 13px | 23px | 13px | 13px |

The relevant primary sources are [attr substitution](https://drafts.csswg.org/css-values-5/#attr-substitution), [substitution guards](https://drafts.csswg.org/css-values-5/#guarded), and [registered relative-unit dependency cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles). The line-height oracle follows the latter's lh back edge and the same existing native invalidation/defaulting path as the pinned typed-cycle tests; it is not based on assuming lh behaves exactly like em. The new tests remain unexecuted. Any disagreement in calibration or original/candidate results must be investigated before accepting the fixture or the repair.

## Validation and limitations

The input proposal's syntax/transport records were read and their sealed payload hashes verified; they were not relabeled as native semantic tests. The supplement's JavaScript syntax and exact scratch patch application passed (execution 45d0f2, exit 0); scratch was removed. No native source, build, index, HEAD, ledger, original repair capsule or sealed keyframe-context proposal was changed. No browser was launched.

I did not add a Lean theorem: an abstract Boolean classifier law without a connection to the native lexer/namespace lookup would merely restate the branch, while the useful obligations here are parser equivalence, SCC edge admission and actual invalidation/defaulting behavior. Shared native parsing plus the original/candidate browser cases are the meaningful validation boundary for this patch.
