# Skipped block-line query WPT draft

**Unrun, artifact-only draft.** No native changes, test installation, build, browser, Git mutation or new comparison harness. Node syntax-only checking passed; no JS fixture execution occurred. Visible calibration is still required on the first real run. The 18 assertions are not predictions that any current candidate passes.

Proposed eventual location: `testing/web-platform/tests/css/css-contain/content-visibility/hidden-skipped-block-line-queries.html`. This package contains that draft, its exact case descriptors/ordered roster and a syntax/static-check receipt. Only the existing two testharness scripts are required; no font/image/timing dependencies.

## Cases and novelty

| Group | Cases | Distinction from existing column eight-case probe |
|---|---:|---|
| Percentage blocks | 6 | No table: query item, inner block or leaf after outer-width or direct item-width change. Separates ancestor resize from directly styled target readiness. |
| Inline line | 4 | Two direct inline-block siblings of the hidden subject, with no intervening whitespace. Query first/second root or leaf in separate fixtures. Later sibling is never rescued by querying the first. Tests why marking only the first frame of a skipped inline line is insufficient. |
| Table-first rescue | 4 | Outer-width/table-width × col/td, deliberately query the table before the selected observer. The existing eight cases do not do this. Both the rescue table rectangle and target rectangle retain strict expectations. |
| Owner boundaries | 4 | One float or one absolutely positioned root/leaf inside the ordinary hidden block. These are bounded controls for traversal through line placeholders and external targets, not assertions that a principal-line marking repair covers them. |

The inline siblings are directly under `.subject`; adding a block wrapper would let first-child-only marking traverse both and destroy this distinction. Root and leaf observers use different fixture instances. The float and OOF cases have definite containing-block widths and no text/min-content contribution. The OOF containing block is explicitly the positioned `.subject`, with left/top zero; no static-position centering inference is needed.

## Exact geometry

All fixture hosts start at (10,10). Outer width is100px, changing to50px only for outer-width routes; outer/subject height is64px. Border, padding and margins do not contribute to observed boxes.

- Block item/inner widths are100→50, height32; the half-width leaf is50→25, height16. Direct item-width changes outer width neither initially nor at change.
- Inline roots are each50→25 wide and16 high. The first stays x10; the second moves x60→35. Their full-width leaves are8px high. Both roots use vertical-align:top, zero parent line-height/font-size, and no whitespace between their tags.
- Table width is100→50, height32; each of two equal fixed-layout columns/cells is50→25. In rescue cases the table's exact rectangle is itself asserted before the target assertion.
- Float/OOF roots are50→25 wide and16 high at(10,10); their full-width leaves are8px high. Only one floating root is present, so no float collision or clearance arithmetic is used.

Every expected array is retained explicitly in CASES.json/HTML, and every visible peer must match it. A peer calibration failure is a fixture/oracle gate failure; do not relabel it as successful bug discrimination or weaken the expected rectangle.

## Read sequence and assertions

Every case uses its own target and visible peer. Stages are warm → hide → change → restore → show; only the target becomes hidden, and both target and peer receive the same width mutation. At each stage:

1. Read only target.outer to flush the parent geometry.
2. In exactly four rescue cases, read target.table.
3. Read selected target first and immediately repeat it, without a mutation or yield.
4. Read the visible peer and, in rescue cases, its table.

Each case's five stage records are produced before that case's assertions (90 records across18cases); `window.skippedLineQueryResults` retains outer/rescue/first/repeat/peer/expected rectangles. All visible and outer calibrations across the five stages are asserted first. Then actual rescue/first/repeat rectangles are asserted. This keeps restore/show evidence available even when change fails. Test cleanup callbacks return no value and remove only their two hosts.

The visible peer is read after the target observations so it cannot preempt the selected query. Outside the four expressly labeled rescue cases, no other hidden descendant or wrapper geometry is read before the selected target. No timers, animation frames or asynchronous interquery yields are introduced.

## Interpretation and remaining gates

A correct table-first rescue with a failing direct cell/column case supports query-target readiness as the discriminator. A failing rescue table itself records that the provider/ancestor is still not made current; it is not counted as a column-only failure. Non-table failures would support the broader skipped-line producer hypothesis. Later-inline-only failures would discriminate first-child-only marking. Float/OOF failures remain separate owner boundaries.

The source hypothesis and offline patch are sealed in css-hidden-ordinary-block-query-audit-v1 (FILES7a4b9fd862582abb6593c08451f74c60ff354c2883492579f22b188b31338a8f). This draft neither imports that patch nor assumes dirty-subtree closure. Existing ordinary-block and column assertions remain useful and are not replaced by these new groups. Root should choose the test subset only after reviewing the current66 results; no all-candidate-pass gate is prescribed here.

No WPT lint or browser validation was run. The source retains standard WPT metadata/help links, exact integer expected geometry and only testharness dependencies. Further wrapping, fragmentation, vertical writing modes, multiple floats, captions and content-visibility:auto are deliberately outside this small diagnostic, rather than silently inferred from it.
