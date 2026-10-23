# Independent hidden layout repairs: browser comparison

Four uninstrumented variants completed. Each ran the same22 files and686 subtests, with19 OK harness ends and3 PASS reftest ends. All four builds passed. All file-end outcomes are unchanged.

| Variant | PASS | FAIL |
|---|---:|---:|
| Baseline |645|41|
| Principal only |679|7|
| Absolute only |652|34|
| Both |686|0|

The exact matrix consists of645 always-passing rows,34 rows fixed by principal marking, and7 fixed by absolute marking. Every repair comparison has zero regressions. The original656 subtests retain their prior outcomes; the28 new diagnostics add four leaf-first failures and two static-position flex/grid OOF failures. All new visible calibrations, actual fragmentation and containing-block ownership controls pass. Raw assertion messages and all pre/post source, binary, test and metadata pins remain retained. Root comparison is in the sibling css-hidden-flex-combined-analysis-v1; the independent boundary review separately recounts all raw rows.

Twenty pending native prototypes were replaced with exact committed HEAD bodies, and AbsoluteContainingBlock.cpp was separately varied. Both native files are installed explicitly for every phase. This demonstrates isolated patch behavior in this branch environment, not execution of a complete isolated upstream checkout. The prior original-key experiment separately establishes the principal repair's preexisting route.

## Timing and interrupted trace plan

The first three timing runs completed with stable inputs and successful cleanup. At256 children, seven per-batch principal-hidden query samples change from[0,0,0,0,1,2,1]ms to[9,11,8,11,10,9,8]ms with principal marking. The corresponding OOF samples change from[1,1,1,1,0,0,1]ms to[7,8,5,8,8,8,7]ms with absolute marking. Each batch sums16 iterations with up to4 distinct leaf queries. Mutation/outer-flush timing remains roughly2–3ms per batch in these hidden configurations.

These are descriptive, fixed-order, integer-millisecond samples, not broad statistical or cost-neutrality claims. All sampled sizes are correct, but positions were not calibrated. In particular the OOF benchmark's centered positions should change with parent width. The sums cannot distinguish one necessary/conservative recovery per mutation from repeated forcing. A first/repeat/distinct-query follow-up with full rectangles is planned before acceptance.

The combined timing run collected84 observation rows and stable hashes, but cleanup recorded PermissionError(1, 'Operation not permitted'). Its leader had exited with-15 and its owned profile was removed; the v1 runner did not record which group signal failed or the PID/PGID. The guard therefore rejected this timing run and aborted before either trace phase. No combined timing acceptance or trace result is claimed. A later read-only process scan found no Firefox command naming that exact profile; this does not authenticate cleanup of every original group member. The rejected observation and error remain unchanged.

## Restoration and limits

The driver's finally block restored all21 native write targets and removed all6 temporary tests, then rebuilt the original working sources successfully. BEFORE and FINAL are identical; root independently rechecked all26 guarded source hashes, HEAD and empty index. The original native prototypes and committed fix103 are restored. Rebuilt binaries are not claimed byte-identical. The driver terminal exit is1 for the retained timing cleanup error, not a failed source/build restoration. There are no recovery errors.

No native repair is accepted or committed by this experiment. Pending gates include exact compact landing files, the separate formal-barrier-led table-column probe, actual absolute-child traces, query cost adjudication and final dependency review. Fix101 remains on landing hold. The broader source/proof callback, dirty-history, provider, ownership and lifetime assumptions remain explicit.
