# Retained CSSOM pseudo-animation controls

Twenty browser callbacks exercise a retained `CSSStyleDeclaration` across animation creation, seeking, cancellation, restart, keyframe-property replacement, retargeting, inherited-font changes and ordered replace/add effects. Every case has a generated-pseudo control. This extends the known bug 1615083 investigation; it does not count seven separate defects or establish a native repair.

## Baseline

The retained #170 browser produced **13 PASS / 7 FAIL**, with harness OK and WPT exit 1. All ten generated-pseudo callbacks pass. Non-generated-pseudo callbacks pass before animation, after cancellation and when the removed keyframe property returns to its underlying value. They fail animated sampling, seeking, restart, the new keyframe property, new-target sampling, relative endpoint updates and additive composition. The individual assertion messages are in `baseline1/TEST-RESULTS.json`; the complete raw log is retained.

Each phase of the creation/seek/cancel/restart sequence has its own callback so an earlier expected failure does not suppress the later observations. Retargeting reads both targets before asserting. The relative-unit callback reads both values, but the failing current-font assertion prevents the initial-font assertion from running for the non-generated case; do not report both assertions as executed.

`run.py baseline1` used the pinned current browser without rebuilding or changing native source. The wrapper backed up and restored the full application and three build/harness extras. Root independently compared the restored application, extras, baseline source and binary hashes, HEAD and index; the temporary WPT, metadata and owned backup are absent. See `ROOT-RESTORATION.json`. WPT lint reports zero problems (`LINT.json`, `lint.log`).

The fixture remains a research artifact until delivered with a self-contained native fix. A composition-only extraction must preserve this baseline; it is not expected to fix these failures. The final CSSOM implementation must address fresh effect properties, context-dependent endpoints, timing, masks, and retained-style cache invalidation rather than special-casing these values.
