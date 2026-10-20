# Table caption percentage-height cache repair: paired WPT

The candidate adds actual ReflowInput containing-block size to the flex measuring
cache key. Its exact 16-subtest WPT has twelve passes and four failures before,
then sixteen passes after. All 354 retained subtests pass in both builds. Eight
existing flex table/caption reftests have unchanged outcomes: seven PASS and one
expected FAIL. No unexpected candidate results occur.

The WPT checks resolved inner table height and combined table/caption extent,
then compares placement and baseline markers with a fresh final fixture. It
covers grow/shrink and restores/repeats updates, with literal-height and
fixed-caption controls. Marker equality alone is not the success oracle.

Both native candidate and restoration builds passed; selected input snapshots
and browser hashes are stable within each run. All non-native/non-binary inputs
are identical across the pair. verify.py authenticates retained inputs and
recounts exact transitions. Source/build were restored, the temporary WPT was
removed, and HEAD/index are unchanged. The prior final-size repair remains
installed on both sides. No isolated upstream browser execution is claimed.

Status: positive candidate evidence; independent review, formal key refinement,
formatting/lint and final packaging remain. Precise internal cache-branch
execution is inferred from inspected source and controlled input changes, not
instrumented. Full allocation/cache freshness remains open.
