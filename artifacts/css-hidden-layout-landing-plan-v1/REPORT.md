# Proposed independent landing-test partition

**Proposal only. No new native acceptance, browser result, or fixture-oracle waiver.** These files are artifact copies. All original sealed diagnostic files, including the 44-case positions file with its absolute-child failure, remain unchanged. The full runtime matrix must retain every failure and calibration before choosing the final patches.

## Suggested packages

| Native repair | Proposed test file | Cases | Purpose |
|---|---|---:|---|
| Principal children after skipped flex child layout | `hidden-flex-item-measuring-reflow.html` | 12 | Original measuring-key route: direct item versus clean leaf, shrinking sibling versus no-shrink/zero-width controls, visible versus hidden; includes insertion and removal |
| Same principal repair | `hidden-flex-fixed-size-query.html` | 8 | Fixed-size exposure with the stronger containing-block key; flex/block, initially visible/hidden, bounding/offset APIs |
| Same principal repair | `hidden-flex-principal-positions.html` | 18 | Item/leaf append/prepend placement without size changes; one/two hidden ancestors with margin/padding/width/height parent mutations; anonymous text Range observer |
| Dirty absolute subtree before its hidden reflow input is constructed | `hidden-flex-absolute-geometry.html` | 4 | Direct absolute-child static-position failure; explicit-offset and visible controls, in-flow insertion and alignment change |
| Same absolute repair | `hidden-flex-oof-descendant-query.html` | 8 | Unchanged leaf-first query corpus: static/explicit, append/prepend, one/two hidden ancestors, percentage leaf after OOF-parent resize |

Principal total38; absolute total12. Keeping three small principal files separates measurement, fixed-size exposure, and placement/anonymous behavior and keeps the Ahem dependency confined to the last file. Principal copies contain no absolute-child test or absolute helper branch. The direct absolute copy has no Ahem dependency. The eight-case leaf file is byte-identical to its diagnostic source.

The first principal file supplies a real preexisting/original-key failure route; do not claim independence from fix101 based only on the fixed-size cases. The second file protects the additional failures exposed by the strengthened key. Conversely, the absolute patch must pass its direct and leaf cases without the principal patch in the four-variant matrix. Shared helper names or a passing combined build cannot establish that independence.

## Mapping and excluded cross-products

`CASE-MAP.json` accounts for all132 original diagnostic names exactly once:50 selected and82 retained only in the larger diagnostic corpus. Every selected registration keeps its original name, stage sequence, geometric assertions, and visible calibration. `DIAGNOSTIC-TO-LANDING.diff` exposes every edit. Loop dimensions are reduced; unused absolute/text helper branches are removed from their respective split files. The direct absolute fixture also drops the unused Ahem stylesheet/font declaration; all its boxes are empty with explicit dimensions. No runtime skip or expected-failure annotation is introduced.

The compact proposal omits repeated offset/prepend sizing combinations, columns embedding that did not demonstrate actual target fragmentation, some API cross-products, two-ancestor direct placement/OOF combinations, and visible-only style/text tests that duplicate the retained tests' explicit visible references. These are packaging priorities, not proofs that the omitted paths cannot regress. Preserve their full diagnostic outcomes and existing regression coverage. A reviewer can restore a case from the map without changing its oracle.

The principal placement file keeps all four parent-style mutations under both one and two hidden ancestors; it does not infer that marking an already-dirty parent guarantees every descendant bit. Anonymous append/prepend remain distinct. Direct absolute and leaf-first tests remain separate because an early parent query can recover state and conceal a clean-leaf failure.

## Pending boundaries and acceptance gates

The additional16 provider/containing-block diagnostics and4 actual fragmentation diagnostics are reserved, not dropped or silently treated as passing. Their mandatory visible calibrations distinguish a bad fixture assumption from a hidden-query failure. They are not imported into these landing files before the ongoing runtime establishes their oracles and source-path relevance. Ordinary hidden containment prevents the conventional external-CB escape; external-to-an-inner-flex ownership must not be mislabeled as outside the hidden boundary.

Before landing either native patch:

1. Reconcile the full raw four-variant matrix, including all calibrated failures. Principal-only must repair its intended direct/leaf/position cases; absolute-only must independently repair its own intended cases. A new boundary failure requires source adjudication rather than omission.
2. Run these exact compact files, whose hashes differ from diagnostic inputs; preserve the expected name roster. They have source/syntax/name checks only at present. Do not transfer browser acceptance merely from their subset names.
3. For independent upstream packaging, retain the relevant old-key route and verify no dependency on a prior fix is accidentally introduced. Stronger-key fixed-size controls can be passing controls in that baseline.
4. Keep the native performance/callback/dirty-history limitations and broader ownership/continuation obligations explicit. This test partition does not close them.

`SOURCE-PINS.json` binds the four retained source fixtures. `SOURCE-CHECK.json` records JavaScript parse/registration and original-name accounting, not executed test success. No production source, test path, browser, build, Git state, or sealed predecessor was modified.
