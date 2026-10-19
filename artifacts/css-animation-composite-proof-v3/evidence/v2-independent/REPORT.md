# Independent full-scope review: animation composite companion v2

## Verdict

**CORRECTIONS_REQUIRED.** V2 fixes the import-closure defect, preserves null computed animation values, and corrects the base-restyle witness. Its history invariant and pending-state model are meaningful improvements. One original obligation remains: the admitted equal-setter path must be connected to delivered readiness/current consumer-cache coherence across sequence prefixes. Current `AdmittedSequence` still accepts an equal skip with stale property/base caches.

This is an artifact-scope gap, not a false Lean theorem or a new Firefox bug. The native repair and independently accepted WPT gate remain unchanged. No producer, Gecko, WPT, browser, build or Git state was modified.

Reviewed producer pins:

| File | SHA-256 |
| --- | --- |
| FREEZE.json | adb5d815a65a02f7dffcec490efcdc238829353ac1bbc02f3604f593aedf5518 |
| INPUTS.json | 754ba30672e3c900885169af1692a1151e4aeeffb4d66985207a7ef29fa3a94e |
| check.py | 5925b020c8197ff2015a479a991ea32dbafa4d768266248c2c88c6ca086f3523 |
| REPORT.md | 08db259a4da87dee3c5d0ac1bcafe3ca78883476b52085239f8866fac41915e1 |

## Remaining obligation and concrete evidence

The unchanged approved SCOPE requires derived offsets and property/base cache validity at unchanged-input skips, or restoration through the relevant real refresh. V2's `Invariant` certifies offsets, properties and base values against historical raw inputs. Its `current` field additionally implies `Fresh` when `pending = false`. Those statements are sound and useful: pending stale caches are no longer mislabeled current.

However, `Admitted` checks only `OffsetsFresh` for an equal-input success. It does not require delivered readiness. Consequently `finite_sequence_refinement` can prove agreement between two states that both retain stale property/base caches. `finite_sequence_cache_contract` is a separate conditional final-ready theorem; it does not prove the required property for admitted equal steps or their prefixes.

The reviewer compiled thirteen additional Lean checks in `CACHE-REVIEW.lean`, combined with the complete producer model and witnesses. All pass kernel checking without `sorryAx` or native-reduction axioms:

1. The producer's concrete stale state satisfies `Admitted` for the equal setter.
2. That setter preserves the stale state.
3. Its caches fail `CacheFresh`.
4. The state is honestly labeled pending.
5. The complete sequence from initial state—successful additive frame, style invalidation, equal setter—satisfies `AdmittedSequence`.
6. That sequence preserves the producer's full history invariant.
7. It satisfies the producer's exact direct-setter refinement theorem.
8. Its final consumer caches are still not current.
9. The new typed geometry action cannot smuggle changes to styleVersion, target or style availability.
10. **The missing ready-path lemma is provable:** from `Invariant`, `pending = false` and equal input, the optimized skip preserves `Fresh`. This uses no premise equating a cache with an expected final answer.
11. Actual delivered style refresh restores current offsets/properties/base and clears pending in the concrete stale-style example.
12. Removing the timeline from a ranged effect leaves stale offsets explicitly pending.
13. Style delivery alone does not incorrectly declare those stale offsets fresh.

The first development attempt needed recursive simplification of `AdmittedSequence` before kernel decision; its log is retained separately. Only the successful final log supplies evidence. The missing-delivery examples are deliberately retained, not removed from the action/native domain.

### Required v3 contract

Keep the all-actions history invariant and pending diagnostics. Add a distinct delivered-readiness admission/dispatch contract for the observable current-cache path. At each admitted equal-setter step, derive readiness from the delivered-action discipline, then prove current property/base/offset coherence and preservation through the skip. Lift that statement to every relevant prefix of an arbitrary finite admitted sequence, including failures, defaults, context refresh, style/target invalidation and delivered style updates.

The condition must describe raw provider versions and actual completed refresh/rebuild dispatch, or a readiness state maintained by the proven transition system. Do not merely assume the final cache equals `buildConsumer`/base output. The generic reviewer lemma shows the existing invariant can supply those equations once readiness is established. Missing timeline dispatch and absent target/style cases must stay explicit; no invented unconditional getter rebuild is acceptable.

Retain nonvacuous pending → equal skip → delivered restore diagnostics, but distinguish that diagnostic sequence from the admitted current-cache observation path. Include ready equal skips, changed setters, default updates, and offset delivery followed by style delivery as applicable. Connect native raw event traces to the modeled delivery conditions, with scheduler timing remaining an explicit external premise rather than a liveness theorem.

`SCOPE-CORRECTIONS-v2.md` calls the original every-skip requirement shorthand and substitutes the pending/history interpretation. This review does not accept that substitution as completion of the original approved obligation. The root's review instruction requires the original full contract or an explicit proved admission/dispatch condition closing it. No native cases or complete extractions need be removed to add that condition.

## Closed correction: authenticated execution closure

The new entry gate checks isolated/no-site/no-bytecode startup before importing other modules. It authenticates the external manifest, rejects duplicate JSON keys and duplicate/case-folded/noncanonical/escaping/reserved paths, scans the exact input inventory, opens regular files through no-follow directory descriptors, and hashes the bytes it copies. No project module is imported during that phase.

The normal process copies only those authenticated bytes into a fresh read-only capsule, then launches a second isolated process. The worker reauthenticates a strict exact inventory before adding the capsule directory to the import path and running the authenticated replay module. The source root's reserved historical `development` and `replay-v2` output directories are not copied or placed on the worker import path. Strict worker authentication rejects them if present.

The full independent replay reran all thirteen producer tamper controls. The prior unlisted `generate/__init__.py` attack now rejects before package execution and before output creation. Modified listed source, extra module/bytecode, malformed/escaping/duplicate paths, file/directory/root symlinks and a shadow standard-library module also reject. The clean control succeeds.

Seven additional independent controls test strict clean admission, an empty unlisted directory, duplicate JSON keys, a case-folded path alias, a reserved manifest path, a reserved directory inside the worker, and a harmless reserved directory at the normal source root. They behaved as intended: only clean strict authentication and the excluded normal-root historical directory succeed. No injected marker executes and no output directory is created in these authentication probes. Results are in `additional-tamper/RESULT.json`.

The trusted checker and external digest still require external authentication. This is not a proof against same-user concurrent filesystem attacks, a compromised Python/OS installation or a substituted unpinned transitive toolchain library. Those limits are honestly documented. Directly invoking the internal replay helper is not the documented authenticated interface.

## Closed correction: raw null computed values

The corrected native provider leaves `AnimationValue` null for null declarations, matching retained `Servo_GetComputedKeyframeValues`. The oracle likewise retains `None`; the Lean provider and entry domains now use `Option Rat`. Actual null entries flow through sorting and segment construction without being replaced by base values. Missing synthesized endpoints remain separate entries with their own replacement operation. Base values remain a separate provider consumed through the complete extracted eligibility/refresh/getter paths.

All original null-provider actions remain. Twelve new cases combine four specified operations with offsets 0, 0.5 and 1. Their base-only style updates preserve null segments, change base values, emit one current restyle without effect-set replacement, and exercise getter fallback. Subsequent removal of the property produces an empty property list. Lean witnesses separately check existing-null operation retention, synthesized missing-endpoint operation and inequality with an actual base-valued declaration.

The fresh replay also compiles the old null-to-base adapter regression. It executes successfully and disagrees with the corrected oracle; no compilation failure or crash is counted. This directly reproduces and closes the previous correspondence defect without deleting its admitted cases.

## Closed correction: current-action restyle witness

`mutant_suppress_base_restyle` now clears prior events before rebuilding with a changed base provider. Its successful kernel witness therefore depends on the current rebuild's restyle. The native mutation check additionally verifies a STYLE action, equal properties/base values between actual and expected observations, no effect-set change, exactly one expected restyle, and equality after removing only that current restyle. Historical events no longer make the witness pass.

## Full-scope audit and replay

I read the full corrected Lean model/witnesses, oracle/corpus, native adapter changes, authenticated checker/replay/tamper code, scope/addendum/correction document, report and bridge. The complete source/extraction obligations from the v1 review were retained and independently rechecked, not replaced by checking only the new summaries.

All 34 full native/provider snapshots are byte-identical to v1. The generator, extractor, mutation definitions, adapter prefix, original SCOPE and addendum are unchanged. All original 662 cases remain byte-for-byte as action records, including errors, signed zero, named ranges, null declarations and random controls. The new cases add coverage rather than replace it.

The reviewer copied only the 79 authenticated source inputs and manifest into a fresh source directory. The v2 gate then created and authenticated its own second capsule. No historical executable was reused. The full replay is terminal exit 0, as is the independent thirteen-check Lean run.

| Evidence | Fresh result |
| --- | ---: |
| Authenticated producer inputs | 79 |
| Complete native definitions | 29 |
| Cases / action observations | 691 / 5,265 |
| Candidate tolerant disagreement rows | 0 |
| Original disagreement rows | 1,458 |
| Candidate rows differing under strict arithmetic comparison | 24 |
| Producer Lean declarations / semantic mutants | 80 / 20 |
| Additional reviewer kernel checks | 13 |
| Producer / additional tamper controls | 13 / 7 |
| Deterministic canonical receipts matching byte-for-byte | 100 |
| Bounded cost samples | 50 |

The 24 arithmetic differences remain within the declared `2e-14` absolute/relative tolerance; sign-bit flags are checked separately. The 100 matching receipts exclude timing/elapsed output and tamper receipts containing run-specific absolute paths.

The independent checker uses the previously reviewed independent lexer/masking extractor to rederive every complete native definition and compare it with the generated body after removing only the declared entry log. Both ordinary setters, complete getter and ordinary computed-keyframe dispatch, record/property equality, ordinary/named offsets and refresh, SetComposite, Build/UpdateProperties, full EnsureBaseStyles/EnsureBaseStyle, computed-value dispatch and every segment/missing-endpoint/equality helper remain compiled. Only the production comparator differs between original and candidate. Provider-definition hashes and all source pins rederive.

The full model retains ordered specified frames, all four specified operations, immutable declaration ownership/content projection, concrete rational offsets, optional raw computed values, stable grouped segment construction, default resolution, properties/base/event state, running/cumulative identities and compute counts. History certificates are mathematical metadata about raw inputs, not added native fields. The geometry action is now structurally separated from style/target changes. Pending invalidation, unchanged skip, actual getter dispatch, actual default dispatch and supplied-style delivery remain independently observed in native traces.

The direct/reference implementations still share the non-setter transition helpers. Their equality does not independently establish the correctness of those helpers; concrete native extraction, independent oracle, source review and explicit invariants provide separate evidence. This distinction is central to the remaining admission gap.

All twenty semantic mutants compile, run, disagree and have kernel witnesses. The original and omitted-composite variant produce identical rows. The skip-recompute mutant stops after its concrete bad-state observation, before an intentionally invalid cache would trigger a later assertion. Cost results are typed harness measurements, not browser performance claims.

## Boundaries retained

The specification snapshots and prior native/WPT report remain authenticated. The native gate is unchanged: 70 new candidate passes versus 52 original failures/18 original passes, plus 340 unchanged existing passes and seven OK harness outcomes. This review did not rerun a browser and does not count WPT results as formal proof.

Ordinary WAAPI is the universal model boundary. JS iteration/reentrancy, parsing and declaration serialization congruence, actual geometry and scheduler delivery, CSS-generated augmentation/override bookkeeping, full Rust value algebra/sampling and rendering remain external. Positive normalized scroll delays are retained in full source/extraction but the numeric corpus fixes delays at zero. Native named-range geometry is bounded and does not vary every named map independently. Rational proofs quotient signed zero and do not establish universal IEEE equivalence. The abstract property identity/order requires an encoding to real property IDs/names. No verified C++→Lean or Python→Lean translation is claimed. Toolchain executable pins do not make all SDK/compiler/Lean libraries hermetic.

## Reproduce

After externally authenticating this review's manifest and checker, run:

```
python3 -I -S -B check.py --expected-manifest <review-manifest-sha>
```

The checker authenticates the closed review inventory, rederives extraction/raw/mutation evidence and confirms all thirteen reviewer theorem receipts. Deliberate symlink fixtures are allowed only at their explicitly recorded tamper-test paths and targets. No project modules are imported. `--replay-output /private/tmp/fresh-animation-v2-review` additionally reruns the complete authenticated producer replay and reviewer Lean checks.

The result remains `CORRECTIONS_REQUIRED` until the delivered-readiness equal-step/prefix obligation is implemented and independently checked in a separate producer version. Frozen v1 and v2 evidence must remain unchanged.
