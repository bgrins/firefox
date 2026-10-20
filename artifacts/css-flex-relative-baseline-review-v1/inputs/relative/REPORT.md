# Relative flex-item positions and exported baselines

## Candidate status

Native build, paired WPT, regression, formatting, and standalone packaging gates pass. Independent native review and the formal companion remain pending; this is not an accepted or committed fix.

## Repair and independence

The two preexisting fallback consumers in PopulateReflowOutput now query GetLogicalNormalPosition. A relative offset must affect the item visually without moving non-descendant boxes through exported baseline alignment. The separate natural-donor candidate introduces a new helper; that helper also uses normal position in its own v2 patch. The shared tested delta changes all three calls. The official two-file patch contains only the two preexisting consumers and the new WPT.

The official relative patch and the natural-donor v2 patch each apply and reverse independently on HEAD 92a6fddf18e5 and upstream 976279105b2e. Applying them in either order yields byte-identical sources and tests. COMMUTATION.json records the exact outputs. The current browser is a shared project build, so this is not evidence of an isolated upstream runtime.

## Evidence

- Original discovery: identical twelve-row release/shared observations, eight nonzero-offset failures and four zero controls; all geometry and removal/restoration controls pass. Normative trace is retained in css-flex-relative-baseline-probe-v1.
- New WPT: 288 cases spanning horizontal-tb/vertical-lr/vertical-rl, outer inline/flex layout, first/last baseline, row/row-reverse/column/column-reverse, text/empty donors, and minus ten/zero/ten pixel block-axis offsets. The paired baseline has 192 FAIL and 96 PASS. The final candidate has 288 PASS; all 96 passing outcomes are unchanged. Every failure was at the final non-descendant-position assertion after calibration and restoration checks.
- Twenty-nine regression files: 23 passing reftests, 309 passing subtests, six OK harnesses. This includes all 48 natural-donor cases on the final shared source.
- The successful native build has no compiler warnings. Mach's preexisting monitor KeyError for export is retained alongside the successful exit and build receipt. The final tested bytes equal candidate.cpp; there is no post-build formatting transfer.
- Scoped native and WPT lint pass without warnings.

## Formal and provider boundaries

The discovery followed source/spec analysis during proof construction, not a completed full-engine theorem. Full normal-position property lifetime, arbitrary-coordinate arithmetic, sticky scroll updates, fragmentation, and orthogonal donor synthesis remain separate obligations. Changing the query does not repair preexisting donor selection or synthesized-baseline policy. The shared candidate contains other pending project fixes whose identities are pinned in the run receipts.
