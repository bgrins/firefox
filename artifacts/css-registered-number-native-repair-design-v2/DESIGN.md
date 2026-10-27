# Registered number dependency repair design

The next release-facing repair should stop creating font and line-height edges from a registered number's unused fallback, or from selected text rejected by its registration grammar. Keep numeric math support. This is a captured-source design, not a compiled patch or an accepted bugfix.

## What is already observed

The authenticated 14-row comparison records seven shared release/local disagreements: unused em, ex and lh fallback; nested unused em fallback; inherited ready provider with unused em fallback; missing provider with selected invalid em fallback; and a wrong-type ready provider with unused em fallback. They return inherited font-size 19px instead of 5px or registered initial 3px. These are one related release-observable dependency family, not seven independently accepted bugs.

The local direct `--n:1em` control additionally returns 19px where release returns 3px. This is a WIP-only regression path associated with the expanded numeric `DependentDataTypes::LENGTH` classification; no controlled revert experiment has proved exclusive causation. Preserve its failed-run evidence. Removing Number from the classification is not a complete repair and risks losing legitimate numeric math dependencies.

## Exact entry points in the captured implementation

1. `VariableValue` parsing unions `fb.references.flags` into its parent's `References.flags`. The data structure explicitly records that flags include nested references. Therefore the root flags are a conservative inventory, not an evaluated dependency set.
2. `traverse` calls `find_non_custom_references` before resolving providers. This initial result is registration-type filtered, but still contains units from unused fallbacks. The WIP widened Number mask makes even a reference-free invalid `1em` enter the graph before typed parsing.
3. `visit_value_references` unconditionally unions `refs.flags` into `value_non_custom_refs`. It also unions flags from a resolved universal provider. The final `registered` edge loop consumes the accumulator without rechecking the registration's syntax. This is a second route around the initial registration filter. It explains why a number with a var reference can acquire font edges even with the release-era mask that excludes Number.
4. The added edge reaches the non-custom node, whose declaration references the registered number. Tarjan then removes the resulting component through `handle_loop`, before the later `substitute_references_with_pending_and_apply` can reject invalid number text or use the valid selected primary. In particular, grammar failure that should affect only `--n` instead invalidates the consumer font declaration too.
5. A separate pending path in `substitute_references_with_pending_and_apply` reparses selected CSS as `VariableValue`, then asks `find_non_custom_references` before `Substitution::into_value` performs actual typed admission. Selected `1em` can therefore request pending font context even though it cannot be a number. Fixing only ordinary Tarjan traversal leaves this path inconsistent.

These are source-supported paths, not instrumented execution traces. The captured cascade contains the used-fallback repair before the raw-nested traversal toggle. That adjacent change does not remove these unit-flag entry points. Rebase any implementation onto the parent's final source role.

## Recommended bounded first implementation

Start with an exact `<number>` registration, without alternatives or multipliers. This contains the reproduced release cases and the eight defensible oracles. Do not quietly generalize to `<length>`, whose explicit Properties API graph rules need separate adjudication, or to arbitrary string/image/color grammars.

Introduce a preparation result that separates substitution and typed admission from computation/publication. Suggested shape, not existing Rust API:

```
PreparedRegistered = Invalid | Admitted { specified, substitution_provenance,
                                        required_context } | Demand(request)
```

Preparation must use the same selected substitution semantics and actual `SpecifiedRegisteredValue::parse` as computation, with the same URL data, property identity, namespace input and attr taint. `AllowComputationallyDependent::Yes` is necessary: `calc(1em / 1px)` is a valid number whose conversion must wait for the font. The parser already separates `parse` from `to_computed_value`, and its grammar alternatives use full-input parsing. Direct `1em` and selected `red` must fail admission; wrong-type primary must not cause the enclosing var fallback to be tried.

For this exact-number slice, derive non-custom dependencies from the admitted numeric expression, including length leaves retained beneath products, inverses and math functions. The captured calc evaluator maps length leaves through `to_computed_value_for_math` with `FontBaseSize::CurrentStyle` and `LineHeightBase::CurrentStyle`; a dimensionless final type does not erase these inputs. Build the collector over the same structural expression representation used by computation. Audit all variants before calling it complete; do not infer dependency freedom from the root type or from a simplified scalar accessor.

The prepared result replaces the conservative unit portion of the accumulator; it must not be ORed into the old fallback-contaminated flags. Keep custom/typed-attribute cycle traversal and context requirements of other registration kinds unchanged. Do not subtract fallback flags: the same unit bit can also come from a used branch.

For the initial implementation, eligibility for preparation requires that every selected provider is resolved and that no selected reference remains in an open custom/attribute SCC. An unresolved stack member is not a missing provider and must not be treated as permission to rescue it with a fallback. If this precondition cannot be established, preserve the existing cycle walk instead of publishing a guessed prepared value. This conservative restriction is expected to cover the acyclic ready/missing-provider reproductions; it does not promise to correct every mixed SCC case.

Add context edges from an admitted preparation while the property is still on the Tarjan stack, before deciding its component. Publish exactly once, only after cycle settlement and context readiness. Invalid admission adds no font edge for the discarded number expression and follows the existing invalid-at-computed-value path; it must not erase an independently established custom/attribute cycle. Cache the preparation for the existing apply point so that attribute reads, URL/taint handling and any parsing or substitution effects are not duplicated. Demand remains a distinct result, not invalidity.

Use the same preparation result in the pending-prioritary path. Admission must happen before requesting numeric context, so invalid selected `1em` settles as the registered initial number without waiting on its font consumer. Admitted length-bearing math requests the actual pending context and resumes computation after completion. Preparation caches require invalidation on provider completion or context restart; do not keep partial results from an interrupted demand attempt.

This is a concrete integration plan, but not a drop-in one-line change. The current substitution operation and apply operation are coupled. A safe implementation must first factor that boundary and prove that the new early call does not mutate the substitution map or publish values before SCC settlement. If that extraction cannot preserve effect and guard behavior, stop and design the unified evaluator rather than invoking the existing apply helper early.

## Smallest useful sequence

1. Factor selected substitution plus typed admission into an owned prepared value; keep behavior unchanged and retain ordinary/pending controls. Preserve CSS-wide-keyword handling before typed admission.
2. Add the exact-number dependency collector and wire it into both the ordinary pre-edge point and pending-prioritary decision. Keep the WIP numeric capability, but stop using raw fallback flags as its semantic evidence.
3. Run controlled original/candidate comparisons with the existing 14-row probe and the eight pinned oracles, including the two font mutations. Only after this passes, create the standalone Gecko patch plus WPT commit. Preparatory tooling remains separate as requested by the user.

A cheaper invalid-literal-only admission check would address the local direct-em regression, but misses the seven release discrepancies. A post-visitor type-mask filter would hide the release symptom but break valid number math. Neither is the recommended main repair.

## Acceptance boundaries and prerequisites

`ORACLES.json` is copied byte-for-byte from the normative trace. Literal number and ready numeric primary yield 5; direct invalid length, selected invalid length fallback and selected red yield initial 3. Noncyclic direct and provider-introduced `calc(1em / 1px)` yield 20, then 30 after font mutation; the width consumer follows. An unused valid numeric-math fallback yields 5 without font dependence. These eight are unexecuted assertion oracles in this artifact.

The self-referential numeric math/font case remains observation-only. The current Properties API explicitly attaches its relative-unit cycle rule to length syntax components; the modern dimension-cancelling number integration is not explicit enough to assert a particular cycle-defaulting result. Necessary noncyclic computation ordering is established; a normative self-cycle default is not. Preserve the existing behavior for that case during this bounded repair and record it without calling it conformance success.

Before implementing, authenticate parser/math sources against the live branch: this design's parser/math copies come from the prior sealed strategy, while the three principal native files are newly captured. A fresh Searchfox fetch failed DNS. Additional prerequisites are a concrete traversal of every admitted numeric AST variant, cache lifetime/demand rollback review, and maintaining guard poisoning and whole-component invalidation for genuine selected var/typed-attribute cycles. Retain attr namespace/taint, raw literal, used fallback and CSS-wide keyword regressions from the existing project. No browser/build, new Lean theorem, production proof, security conclusion or normative coverage credit is claimed.
