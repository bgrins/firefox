# Preserve cancellation when shrinking large measured flex bases

The local repair fixes all 18 previously failing WPT cases and all 12 new failing flex-API assertions. A content-measured base can exceed the preferred coordinate range even when the final requested size is small. The old distribution clipped the adjustment before adding it to the base, leaving a nominal 1000px item millions of pixels tall.

The candidate computes base+sizeDelta in AuCoord64, then narrows that sum to the full signed32 storage interval. It deliberately does not clip the sum to the smaller preferred interval: doing so could hide a max-size violation from the following freeze decision. The optional ComputedFlexItemInfo delta is widened to int64 and captures the requested sizeDelta directly, before min/max clamping. FlexItemValues converts that value to CSS pixels without an intermediate nscoord conversion.

The standalone patch contains three native files, the 24-case WPT and a focused addition to the existing chrome flex-API test. The chrome test is necessary because getAsFlexContainer is privileged; it checks measured bases, requested shrink deltas beyond signed32 app units, and final dimensions. No WPT metadata is changed. Research remains outside this patch.

## Actual validation

| Check | Result | Terminal evidence |
| --- | --- | --- |
| Original new WPT |18 FAIL,6 PASS; harness OK|50742/81b0ac, exit1 in assessment capsule|
| Original focused chrome test |12 FAIL,91 PASS assertions|50919/827fe5, exit1|
| Native build binaries |PASS|4488/a51eba, exit 0|
| Corrected complete WPT run |235 PASS assertions;27 PASS/OK file outcomes|38964/1d7bed, exit 0|
| Full chrome flex API directory |538 PASS assertions;7 PASS files,545 checks|68269/363133, exit 0|
| WPT lint |0 problems|13769/b97ec4, exit 0|
| Chrome JavaScript lint |0 problems|21328/774dec, exit 0|
| Scoped native formatting |3 issues fixed; no errors|19703/29123d, exit 0|
| Four standalone patches |4 individual cases and all 24 orders apply/reverse;400 commands|83831/af2e37, exit 0|

The complete WPT run includes the 28-case total-violation test and all 24 new measured-base cases. Six existing flex-shrink files extend the preceding 20-file preservation suite. Build output includes a nonfatal mach resource/tier-reporting KeyError; the build exited0 with successful compilation/linking and both test suites executed the resulting browser. Native source, browser and tests are pinned in AFTER-INPUTS.json and AFTER-2-TESTS.json. The obsolete mach clang-format entry point failed before formatting; the supported scoped linter was then used. The first patch-check script stopped before applying anything on an unexpected Git diagnostic for untracked files; its source/failure receipt is retained.

## Review and limits

Independent source review confirmed that reverse-loop indices track original items even across frozen entries, the early break does not cause an invalid access, and both old and new diagnostic writes have the same available-space and nonzero-weight guards. Zero-share active items receive zero in both implementations. Frozen items retain their earlier diagnostics. A proposed stale-delta concern was withdrawn after checking the exact old brace nesting. The raw64 delta agrees with the field's documented unconstrained requested-change meaning.

This is a focused native repair, not complete verification of flex sizing. The accepted conditional Lean base<=preferredMax theorem remains unchanged and does not cover the reproduced producer. The separate [boundary proof review](../css-flex-measured-base-boundary-root-review-20261111-v1/REPORT.md) independently accepts the exact mathematical cancellation counterexample, a representable-target/reporting lemma and an outside32 aggregate-sign counterexample. The wide-addition/provider bound, floating sizing and full native correspondence remain open. Saturating a truly unrepresentable signed32 target can still alter the aggregate violation sign; the repair must not be presented as a proof of those larger semantics. No memory-safety or performance claim is made. Tentative priority P3 for extreme-size layout correctness.

The patch applies independently to HEAD and composes in every order with the prior signed-wrap, margin-sum and total-violation patches. This is patch-transport evidence, not a clean-upstream runtime comparison. Validation ran on the current branch with those repairs present. All temporary patch-check trees were removed. The existing objdir remains useful and was retained.

## Evidence correction

The first candidate WPT command accidentally retained the preceding repair's --log-raw option while adding a new one, and omitted that suite's first test. It ran 26 files successfully, but overwrote css-flex-total-violation-repair-20261111-v1/after.raw.log. LOG-INCIDENT.json records both hashes and the exact cause; misdirected-after.raw.log preserves the misplaced output. The old raw log is no longer authenticated and was not reconstructed or silently refrozen. Every other file in that historical capsule, including its original structured report and console log, still matches its original manifest.

The authoritative candidate validation is the corrected 27-file rerun, with independently checked test selection, exactly one raw-log destination and fresh exclusive output paths. It includes the omitted total-violation test. The old capsule's original FILES.json remains unchanged so its integrity failure remains visible. This incident does not change native source or the previously accepted Lean proof bytes.

Validated locally and kept as a separate five-file patch. No commit or push occurred; signing availability is unchanged.
