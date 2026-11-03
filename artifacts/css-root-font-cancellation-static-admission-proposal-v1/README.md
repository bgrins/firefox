# Narrow static-admission proposal

This is a two-file source proposal for a future diagnostic owner, not an executable or activated owner. Sealed four-role preparation 38aeafaa and the running archive owner are untouched. candidate/baseline.py and candidate/run.py are intended to replace the corresponding files together in a newly reviewed successor, with new exact deltas and owner/input pins.

## Exact repeated work

The current driver calls baseline.prepare, then baseline.require_ready, then baseline.guard, whose first statement calls require_ready again. Each performs the same check.validate_policy over immutable saved evidence. That validator calls admission.validate_current, which invokes adapter.native_head_view and then separately requires adapter.validate_refresh to equal the captured snapshot. The native-head routine itself invokes validate_refresh. The later live baseline.observe also calls native_head_view.

The proposal retains prepare and its full validate_policy exactly once at the top level. require_ready keeps all three activation/current-binding gates, but replaces its semantic replay with fresh byte/closure authentication. The expected owner manifest is passed explicitly from the driver's original argument into require_ready and guard. No global cache, session cache, monkeypatch, recorded result reuse across processes, or hand-copied native-head implementation is added.

Both existing readiness boundaries remain. Each authenticates the original manifest digest and every owned payload, requires the current POLICY bytes to decode to the same policy object, recomputes the unchanged complete external-input closure from pinned role/capture/source/suite data, compares it to the admitted consumed-input map, and rehashes every present input or requires the recorded absence. Dangling links do not satisfy an absence pin. Changed evidence rejects before entering the live guard body; matching unchanged bytes preserve the prior semantic decision.

## Guards that remain

- prepare, current_capture, observe, require_role, metadata_guard, require_app_inventory and environment are byte-identical functions.
- guard changes only its signature and first readiness call. Its remaining body is AST-identical: full snapshot equality, native signature checks, canonical controls/role/pins, source and accepted-payload identity claims, flags, application metadata, binaries and returned live verification closure remain.
- observe still performs native receipt/refresh validation and actual Git signature/ancestry/two-file checks, source-to-HEAD hashes, canonical and additional inode claims, source-context pins, quiescence/lock absence, flags and full current-state observation.
- run.py changes only two calls to pass the original manifest argument. Input binding, pre-mutation verification, all source/application/index/flag checks, build/WPT/archive steps, publication failure accounting, backup handling, finally restoration and RESULT remain byte-identical.

No live read is replaced by saved state. The old second and third top-level semantic invocations are replaced by complete evidence reauthentication at their same locations. This relies on the saved validator being a predicate over the authenticated inputs; its unchanged native live observations continue later. The proposal does not make mutable native state an immutable input or remove a cryptographic signature check.

## Residual cost

admission.py is unchanged. Its native_head_view call and the separate validate_refresh == capture.snapshot join remain. baseline.observe's native_head_view call also remains. The exact currently pinned capture adapter's validate_refresh calls its parent.validate_refresh and the completed refresh driver's saved(policy), so historical saved evidence can still be revisited. This package neither changes those APIs nor establishes a general complexity bound. It only reduces the three top-level validate_policy invocations to one; it does not claim one total refresh validation or a measured wall-time improvement.

The executed independent audit calls baseline.prepare and therefore still gets its own semantic validation. The only known runtime caller of guard is updated here. A future caller must pass its authenticated manifest explicitly; omitted/mixed signatures fail closed. Existing sealed capture adapters continue to use their own unchanged source.

## Focused checks

The checker extracts actual prepare/require_ready functions, the driver admission prefix and guard's first readiness statement. It uses the real ownership authenticator and closure function on tiny owned files. The semantic validator is an explicit counting double, and the native live body is not executed. Source comparisons separately establish that the live body and observer are unchanged; these tests do not simulate native correctness.

Both --run and --check prefixes perform one semantic validation. The run path also performs both pin rechecks before its live-body marker. Ten rejecting cases cover changed owner code/manifest, external evidence, capture, capsule manifest, introduced file, dangling absence link, policy-object mutation, a closed gate and a change between readiness boundaries. The last case first passes one pin check, then rejects at the second. Owned scratch is removed. An initial harness run did not catch the real authenticator's RuntimeError; CHECK-INITIAL.log preserves that harness failure, and the corrected checker catches that existing rejection type. Candidate code was unchanged by that harness correction.

No saved full lineage replay, unchanged stream/staging/archive suite, native build, browser, source/app/index/canonical mutation or signing occurred. The proposal requires source peer/root review and fresh binding in a future owner before any use.
