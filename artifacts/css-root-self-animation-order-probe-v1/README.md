# Root animation calibration-order discriminator

This unrun probe separates root-identity conversion from calibration cancellation and ordinary-comparator reset ordering. It preserves both sealed WPT versions and the actual corrected-v2 result. The read-only assessor reports control validity separately from normative target comparisons; no overall native acceptance gate is defined.

## Actual evidence and limits

Independent saved replay 4d3fe4/0 matches the entire v2 raw assessment: 8 FAIL/6 PASS. The failed callback messages expose first reads only: root rem 128 vs 32, existing child/root-pseudo rem 64 vs 46, CSS root rem 46 vs 32, root rlh 74 vs 38.4, root line-height rlh 153.6 vs 38.4, CSS/substituted root rlh 74 vs 38.4. The six PASS callbacks include substituted root rem, but this establishes only that its assertions passed. Its exact raw numeric observations were not emitted. The failed cases also collected settled values in window.rootFontSelfObservations before asserting first values, but those values were not archived in WPT raw output. No settled-state conclusion follows from a failing first assertion.

The v2 WPT differs from the earlier calibrated connector probe in two concrete ways. The earlier probe reads restored root fontSize and lineHeight after cancelling its em calibration, before creating the target effect. It also computes ordinary references in a separate frame. The WPT does not read after calibration cancellation; for root tests it temporarily changes the same root to an ordinary relative value, reads it, resets the declaration and creates the effect without another root read.

Child/pseudo rem 64 is consistent with the prior em calibration's 32px root base, not the configured 23px base. Larger root 128 and line-height 153.6 values are consistent with feedback, but neither cached Device contents nor the number of native recomputations was logged. They are not proved causes. Substituted rem PASS must not be taken as proof of a separate correct root identity: the exact e86 WithVariables arm recursively invokes AnimationValue::from_declaration with the same Context. Substitution/ordinary cascade work can differ in ordering, but its role here is unestablished.

## Discriminating experiment

There are 34 fresh-frame cases and 68 target samples. Each frame first measures initial rem/normal-rlh, configures the literal underlying root 23px/37px and records both root computed values and independent 100-unit metric proxies. No earlier frame's root animation survives into a later case.

For rem and rlh, the targets are root font-size, existing-child font-size, newly-created-child font-size, root-host-pseudo font-size and root line-height. Root font-size additionally has clean, em-cancel and ordinary-comparator/reset histories. Child and pseudo targets have clean/em-cancel histories. Root line-height has clean/comparator-reset histories. Each disturbance has two separate lanes: no intervening read, or an explicit root fontSize/lineHeight precondition read. Em cancellation and comparator reset are never combined in this experiment. New-child creation happens after cancellation/reset and after any explicit precondition getter.

After creating the target effect, its property getter is first. Both first and settled target samples are collected before effect timing inspection and post-state root/metric proxy reads. The explicit-root-read lane records whether its underlying 23/37 precondition actually held, without discarding target readings if it did not. Post-state probes cannot retroactively establish a pre-effect Device value. Full errors, calibrations, first/settled values and cleanup are returned.

Interpretation is bounded: a no-read/read difference supports an ordering interaction; it does not establish the native cache or refresh mechanism. A fresh clean root mismatch remains separate root-self evidence. Existing/new-child differences expose target creation effects. Uncalibrated lanes retain their observations but cannot support a normative comparison. These observations may justify a future fixture that explicitly verifies restored underlying state, while cancellation-to-new-effect behavior remains a separate regression target. This package makes no change to v2 expectations and accepts no root-identity patch.

## Execution contract

Root may evaluate the exact saved probe.js as an async JavaScript expression in the chosen archived-original browser, on a loaded same-origin-capable HTML document with a body and no restrictive CSP. The script creates and removes its own iframes and cancels all effects; it does not navigate the outer page. Root retains responsibility for archive inventories, profile/process cleanup and recording the exact script hash/browser identity. No browser was launched during preparation.

Save the complete returned object, then replay the read-only assessor:

```
python3 -I -S -B artifacts/css-root-self-animation-order-probe-v1/assess.py /absolute/path/to/REPORT.json > /absolute/path/to/ASSESSMENT.json
```

Final saved 9ddbf8/0 passed JavaScript syntax, the exact 34-case roster, five synthetic result paths and 12 malformed-record rejection controls. The paths include ordering differences, a persistent root mismatch, uncalibrated precondition readings retained, and first-only versus settled differences. Synthetic checks are assessor tests, not browser evidence. No native source/app/index/canonical operation occurred.
