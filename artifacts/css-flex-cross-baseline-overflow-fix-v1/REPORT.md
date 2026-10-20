# Flex baseline cross-size sum repair

## Native change and browser evidence

The final two baseline-group sums in `FlexLine::ComputeCrossSizeAndBaseline` now use signed64 intermediates. Their maximum with the ordinary-item size is capped at nscoord_MAX before storage. Per-item sizing, baseline providers, group selection and offsets remain unchanged.

The new 54-case WPT has a directly paired result of 12 FAIL/42 PASS to 54 PASS. Every failure reaches the final 100px container-height assertion after width and computed size/margin controls. All 42 passing status/message pairs are identical. Only nsFlexContainerFrame.cpp and the two browser binary pins differ between runs. The release 158 and shared 160 discovery probe independently reproduced the same zero-height cases. Inputs require extreme numeric dimensions; a tiny tree suffices.

Build succeeds. All 29 regression files pass, including existing first/last baselines, three single-line min/max clamp tests and the pending collapsed-donor WPT. There are 26 successful reftest endpoints and 63 passing subtests in three testharness endpoints. Native and WPT lint have no warnings or errors. The tested source and final formatted source differ only in two explicitly verified whitespace edits; FORMAT-TRANSFER.json and SOURCE-ROLES.json retain that correspondence. No fresh build is attributed to formatting-only edits.

## Formal result and limits

Six kernel results prove signed64 addition safety for arbitrary signed32 operands, nonnegative bounded storage when the ordinary maximum is nonnegative, preservation of any subsequent finite maximum clamp, identity below the cap, the absent-group case and the calibrated browser witness. The exact extracted repaired body passes eight UBSan executions across O0/O2, including the old overflow inputs and exclusion/smaller controls. Four discovery lemmas and the original native failures are retained separately.

These proofs cover the changed sum/maximum/storage operations. They do not prove all cross-axis sizing, frame/provider correctness, earlier subtraction safety, final overflow geometry, compiler correctness or the whole flex algorithm. The model's integers and source expression correspondence remain explicit. The standalone and combined source roles share the exact selected body apart from verified formatting; no standalone upstream browser build is claimed. Independent native/formal review remains pending.

## Packaging

`fix-candidate-v2.patch` contains only nsFlexContainerFrame.cpp and flexbox-baseline-cross-size-overflow.html. It applies/reverses on HEAD and retained upstream, excluding the allocation and baseline-donor repairs. The patch SHA256 is c5a8e37b6f7fb142b62bcc8a963371b141e926dde290e10bee7731b47c4aec56. Native executables from extracted checks were removed after successful terminal runs; the shared Firefox build remains available.

The current [Flexbox cross-size algorithm](https://drafts.csswg.org/css-flexbox-1/#cross-sizing) supplies the baseline maxima and single-line min/max clamp used by the 100px WPT oracle. Discovery, proof/tooling and review evidence must precede the separate native/WPT commit. Signing is currently unavailable; no accepted-fix or committed-fix count increases yet.
