# Relative overflow positioning: source-bound formal companion

## Verdict

**BOUNDED_SOURCE_CORRESPONDENCE_PROVED; HOLD_FULL_LIFECYCLE_SCOPE.** The proposed native repair has separate positive browser evidence and an independent bounded native review. This companion proves the declared integer/source-coordinate relation through actual-size commit and subsequent relative-position updates. It does not promote unresolved predecessor-property, callback, skipped-path or full observer/lifecycle obligations to unconditional acceptance. All seven original requirements remain in FORMAL-SCOPE.md; their disposition is below.

The artifact binds the original tested two-file patch f7d213934f10ac0c33fbffe999630f45516f6e3836ca23abb1bfdcc658cd6b04 and candidate CPP d80f991771f48292657a7c9e5914394adfa30c93e55fa5b3f5626567db5de197. Root's later formatting-only linebreak transfer is a separate packaging bridge, not byte-identical source claimed here. Original140 WPT remains the standalone test; supplemental280 RTL cases do not replace it.

## Source and mathematical correspondence

SourceGeometry.lean models the actual two-dimensional conversion branches from WritingModes.h, optional NormalPositionProperty/getter fallback, selection of normal inline coordinate before reflow, arbitrary returned physical size, current physical offset, size installation before conversion, normal-property storage, physical offset application, logical conversion and final logical-rect conversion. The latter executes start+size before subtracting the end from the container; its intermediate bound is explicit. Current and previous sizes or offsets are not assumed equal.

The key theorem helper_commits_actual_size_and_offset establishes the actual returned size, unshifted stored normal and exactly-once physical offset. update_uses_committed_normal joins that state to the actual RestyleManager cache/update logic. Repeated-update and finite-continuation-chain results preserve initialized properties. The frame-aware relative guard implies the real downstream applicability check, and the actual Default nonrelative/sticky branches preserve their original coordinate semantics.

The actual source is not itself translated and certified by a C++ compiler proof. Exact source extraction, manual correspondence, compiled calibration and semantic challenges support the translation. This distinction is explicit; a Lean theorem does not automatically certify arbitrary native source or allocation behavior.

## Full original requirement disposition

| Requirement | Result | Remaining boundary |
| --- | --- | --- |
| 1. Applicability, flags and actual callers | Derived relative→downstream guard, six Default callers authenticated, nonrelative/sticky model preservation | Hypothetical NoMoveFrame is outside actual caller roster; callback-time frame/style validity remains an engine contract |
| 2. Predecessor origin and normal property | Getter faithfully preserves absent-property fallback; existing-property used-position independence and per-step initialization proved | Correct unshifted first-predecessor property across all layout/style/reparenting paths is not proved |
| 3. Coordinate transfer and machine operations | Full two-dimensional branches, independent actual sizes, exact rect-end arithmetic, explicit ExecutedDomain and derived sufficient small-input domain | No universal native provider bounds; retained before/candidate overflow witness rejects final-fit-only safety |
| 4. Offset provider and commit | Arbitrary current physical offsets and actual returned size flow through exact extracted Finish/Apply routines; normal/used commit theorem | Full percentage/auto offset resolution, arbitrary child callback and retained-overflow side effects are provider boundaries |
| 5. Dynamic cache join | Exact cache/default/store/update slice; initial/update equivalence, repeated update, return to zero primitives | Eligibility/lifetime and arbitrary intervening mutation outside selected update path remain explicit |
| 6. Lifecycle and observers | Existing skip/list/status code unchanged; base/override DidReflow source inspected; browser lifecycle/regression evidence retained | No universal skipped-path initialization, arbitrary frame graph or complete overflow-observer closure |
| 7. Replay and controls | Genuine before/candidate slices, source/tool pins, kernel/compiled mutants, manifest-only relocation and integrity controls | Native browser environments are authenticated evidence, not replayed by the proof checker |

PROVIDERS-AND-ADMISSIONS.md names the exact source/provider boundaries and why each matters. The full lifecycle verdict stays HOLD; the original scope has not been reduced to a statement that all test rows pass.

## Native extraction and calibration

build_native.py extracts exact logical point conversion methods, normal getters, both ApplyRelativePositioning overloads, complete FinishReflowChild, LogicalRect::GetPhysicalRect, genuine before/candidate selection/finish slices and the RestyleManager cache/update statements. EXTRACTIONS.json records their hashes. Facades supply frame/property storage, actual callback size and physical margins, and explicitly replace unrelated engine callbacks/overflow-storage machinery. Earlier point-only calibration is retained as development history after the real rect-end composition was added.

The final independent integer oracle covers216 combinations across six effective mode/direction variants, static/relative/sticky style, property presence, offsets and unequal/empty actual sizes. Genuine before and candidate each match their respective semantics at O0 and O2:864 ordinary executions. Four compiled mutants are detected at both optimizations: retaining used inline start while applying offsets, omitting application, using shifted position for cached updates, and ignoring actual returned size. These are semantic output failures, not intentionally broken compilation.

A further source-sized case fails UBSan for both before and candidate at O0/O2: logical end2147483647+1 overflows although the abstract final coordinate is−1. The kernel preserves this counterexample. It is a preexisting arithmetic boundary, with no browser reachability or new bug-count claim. Neither passing ordinary cases nor cancellation in integer algebra erases it.

## Kernel and replay controls

Twelve preliminary results are retained in RelativeOverflow.lean; SourceGeometry.lean adds21 source/coordinate/domain results. All33 are checked against the allowed axiom set propext, Classical.choice and Quot.sound. Four independent false claims challenge missing block offset, ignored actual size, used-position cache update and final rect-end safety. Two forbidden-axiom controls reject injected assumptions and sorryAx.

verify.py enforces exact source roles and a closed roster, rejects extra compiler caches even after a manifest is resealed, and supports a fresh manifest-only relocated replay. run_integrity_controls.py also rejects modified source and resealed candidate/baseline substitution. run_checks.py rebuilds extracted source deterministically, validates tool/provider identities, compiles kernel results, performs negative controls, checks the WPT script, applies/reverses the standalone patch, recounts browser logs and executes native source calibration. Temporary compiler products are removed. Receipts identify completed replay runs.

## Authenticated browser evidence

Both complete outer browser capsule rosters and every payload hash were authenticated before selected raw receipts were copied. Tested before/candidate CPP, patch and WPT identities match this companion.

- Original runtime:193 payloads,140 subtests,110 PASS preserved and30 FAIL→PASS (16 initial translations,14 updates). The35 retained regression files are unchanged:24 PASS,10 expected FAIL and the separate final-size WPT file with336 PASS subtests.
- Supplementary RTL runtime:304 payloads,280 subtests,220 PASS preserved and60 FAIL→PASS. The61 nonflex files remain unchanged:24 PASS,36 expected FAIL,1 OK. Expected failures are retained as failures.

recount_runtime.py independently checks these raw transitions and unchanged file results. Both root experiments restored source/build. Runs used the shared combined tree, not an isolated upstream runtime. Root's final formatting/lint evidence and the independent reviewer remain separate acceptance inputs.

No production source, WPT tree, index, browser or main build was mutated by this agent. This is a source-bound companion with explicit scope limits, not a proof of all CSS fragmentation or all-coordinate native memory/arithmetic safety.
