# v1 to v2

## Why v1 was insufficient

The old `ordinary_run_refinement` invoked `arbitrary_actions` on `ordinaryPlan`. It proved the evaluation of a drawing plan, but did not prove that actual-shaped run selection, boundary shrinking and partial-ligature dispatch produced that plan. `shrink_refinement` and `unitOffset` were not connected to that theorem. The 887 extracted-native cases supplied finite evidence, not the missing universal connection.

V1 also explicitly excluded negative total ligature advances. The later calibrated browser experiment establishes that those advances are reachable. V1's exclusion is retained as historical evidence; it is not erased or retroactively widened.

## Correction

V2 starts from raw words, detail records, spacing inputs and original text-unit indices. It derives classification flags, preserves the original shape/metric domain through those updates, selects font runs using the actual binary-search shape, shrinks with explicit forward/backward index loops, scans raw ligatures, and executes the actual-shaped per-unit cluster fold. The independent reference groups raw cluster flags and computes ordered emissions from prefix sums. It does not receive an expected eligibility answer, output plan, final coordinate or event list.

The top contracts are `TextInput.original_input_complete_dispatch`, `NativeDomain.actual_length_complete_dispatch`, `Ordinary.complete_raw_dispatch` and `Identity.simultaneous_raw_geometry_identity`. Their helper chain includes actual raw predicate ordering, adjacent/last run relations, selected-range bounds, shrink bounds, positive scanned denominators and count/product bounds. The old plan theorem remains a nonnegative historical control; it is not used as the new top-level native dispatch argument. Working directly in unit indices removes the old unconnected cluster-index/unit-offset conversion.

## Preservation

- The original PUA classifier snapshots, approval, primary CSS/Unicode evidence, actual ICU tables, complete classifier/setter/draw extraction, all887 cases, all17 mutations, invalid inputs and source-only caller inventory remain.
- The old v1 input closure is recorded in `V1-BASE.json`. Frozen v1 was not edited.
- Existing positive/nonnegative behavior is checked independently under both arithmetic policies. The signed repair is a separate root-authored native change; it does not become part of the PUA-only production patch.
- The native observer adds only `drawUnits.push_back(idx)` immediately before actual emitted mark calls. Each extracted body has its original identity plus an observer identity. Removing the insertion reproduces the exact extracted/mutated body. It supplies no expected eligibility or geometry.

## Added gates

Raw-word setup/decode and original-input admission kernels; ordered native draw identities; full raw dispatcher mutation counterexamples; signed/legacy and original/PUA separation; ASCII controls ensuring the negative-only geometry checks are nonvacuous; full uint32 count-domain arithmetic rows; five compiled arithmetic mutants with matching kernel inputs; pinned numeric type providers and finite exact-operation domain checks; independent SFNT/font/WPT review; fresh closed canonical and relocated replay.

These additions preserve the distinction between universal mathematical refinement, finite extracted C++ agreement, source-only external consumers, and root-owned rendered evidence.
