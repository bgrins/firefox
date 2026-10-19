# Computed registered initial-value provider

## Finding and status

The helper `remove_and_insert_initial_value` places a registration's specified initial tokens inside a `ComputedRegisteredValue::Universal`, including for typed registrations. The ordinary cascade publishes that wrapper without computing it. This is a provider representation defect independent of the keyframe conversion limitation repaired by fix 70.

Root's retained ordinary browser run has **3 FAIL, 3 PASS, harness OK**. With a registered `<length>` initial value of `1in`, both fallback-to-initial cases and inherited direct `initial` serialize as `1in`; all must serialize as `96px`. Noninherited direct `initial` and both literal-length fallback controls pass. I inspected the raw rows, not only root's summary. Root's separate keyframe diagnostic has **1 FAIL, 4 PASS, harness OK**: a midpoint from 14 to a fallback initial number of 10 returns 10 instead of 12. Its broad animation path is not part of the proposed standalone WPT.

`native.patch` is an artifact-only two-file proposal. It has not been compiled or executed. No production file was changed here. `proposed/registered-initial-computed-value.html` is the exact six-case ordinary probe subsequently installed and run by root. Root owns runtime identity/build receipts; this capsule retains the raw browser logs and source snapshots rather than claiming a new independently executed browser gate.

## Spec trace and independent oracle

Scenario: a valid registered length with initial `1in`; the child is explicitly reset, or its missing-variable fallback resolves to the sole keyword `initial`. The parent's registered value is `192px`, so inheritance cannot accidentally satisfy the expected result.

1. [Values 5 property substitution](https://drafts.csswg.org/css-values-5/#substitution-in-properties) treats a sole CSS-wide keyword after substitution as if originally specified. Thus the missing-variable fallback must take the same initial-value path as direct `initial`.
2. [Properties and Values computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time-behavior) computes registered dimension values into their canonical units. [Absolute lengths](https://drafts.csswg.org/css-values-4/#absolute-lengths) fix the inch/pixel ratio, yielding `96px`.
3. CSSOM obtains this registered computed value; the ordinary test checks its serialization. Existing `registered-property-initial.html` independently tests the same `1in` to `96px` conversion for default values, but does not exercise these explicit resetting routes.

**REACHED:** the ordinary three failing observations violate the typed initial-value computation requirement. This conclusion does not require a same-effect animation dependency or a compositor assumption.

Spec evidence was retrieved on 2026-10-19 using primary draft pages. `webspec-index` is unavailable and direct Python retrieval failed DNS; retained web-tool responses identify the URLs, retrieval requests and passages. No automated HTML-id validator ran. No unlanded specification change is assumed.

## Exact source chain

Full files under `source/` are pinned in `SOURCE-PINS.json`.

| Stage | Complete native definition and conclusion |
| --- | --- |
| Initial preparation | `PropertyRegistration::validate_initial_value` rejects references and invalid/dependent typed initial values. `compute_initial_value` parses typed values with `AllowComputationallyDependent::No`; universal syntax deliberately remains universal. |
| Cache publication | `Stylist::rebuild_initial_values_for_custom_properties` builds a fresh map, honors script-registration precedence, computes each selected registration, skips failed computations, then publishes map and flags. |
| Default seeding | `Cascade::init_custom_properties` uses the computed cache for root inherited values and noninherited values. |
| Direct override | `Cascade::cascade_custom_property` skips the already-seeded noninherited direct initial, but inherited direct initial calls the defective helper. |
| Substitution override | `substitute_references_if_needed_and_apply` recognizes the substituted CSS-wide keyword, calls the same helper in initial-defaulting branches, and returns before ordinary typed `Substitution::into_value` computation. |
| Finalization | `finish_cascade_custom_properties` shrinks/reuses maps; it does not reparse universal wrappers. Graph traversal's final substitution call does not perform a second typed conversion. |
| Observable consumer | `Servo_GetCustomPropertyValue` obtains `get_for_cssom`, resolves/clones and serializes the stored value. `ValueInner::Universal` preserves the raw value. `to_variable_value` likewise returns universal raw tokens instead of canonical typed serialization. |

Searchfox discovers exactly one helper definition, its import, and two call sites; exact local reads confirm the same roster. Searchfox's indexed text is older than these local snapshots. Installed CLI does not support `--permalink`; names and complete pinned files are used instead.

## Minimal repair

Add an `initial_values: &ComputedCustomProperties` parameter to the helper. Remove the old entry, then clone `initial_values.get(registration, name)` if present. The substitution caller passes `stylist.get_custom_property_initial_values()`. The cascade caller already holds `initial_values` from that getter.

This preserves:

- The registration's specified initial tokens, including `CSSPropertyRule.initialValue`; no descriptor mutation or early parse-time normalization.
- The inherited/noninherited bucket chosen by the actual registration.
- Universal registered values as universal, and missing initial values as absent. A failed cache computation is not replaced with an uncomputed typed wrapper.
- Existing CSS-wide branch selection, inherited-value handling, and `handle_invalid_at_computed_value_time`. Revert-policy TODOs are unchanged.
- Typed value, URL context, and taint fields by cloning the actual computed provider value.

The helper borrows the immutable stylist cache and mutates only the builder's separate substitution map. The cascade caller already combines these borrows elsewhere. No new imports, callback, threading operation, lazy computation, or provider allocation beyond ordinary value cloning is introduced. Compilation still remains root's gate.

## Initial-value readiness and taint boundaries

The inspected cache rebuild callers are `Stylist::flush` after stylesheet cascade-data rebuild, successful `register_custom_property` after validation/registry insertion, and `Servo_InvalidateForViewportUnits` when recorded initial-value flags require recomputation. `new_for_initial_at_property_value` supplies the intended initial computation context. Ordinary cascade already adds `get_custom_property_initial_values_flags()` to the style. The repair uses that established provider/readiness boundary; it does not prove every invalidation scheduler or allocation path universally.

Registration validation forbids substitution references in initial values; typed initial computation uses default empty attr taint. The existing CSS-wide defaulting helper also discards the incoming substitution's taint when replacing it with a registration initial value. Cloning the cached initial preserves this policy and the cache value's actual taint field. The normal typed-substitution taint path, inherited-value taint, and the recent universal conversion taint repair are unchanged. This is not a proof of all attr-security/defaulting semantics. Existing `attr-css-wide-keywords.html` and attr-tainted animation/security tests remain useful regression gates.

## Standalone applicability and fix 70

Fix 70 changes `Servo_GetComputedKeyframeValues` to consume the completed custom-property map for typed unparsed keyframes and exposes `CustomAnimatedValue::from_computed`. It deliberately leaves generic `from_declaration` behavior unchanged. That exact patch is retained as context only.

The ordinary six-case probe never calls keyframe conversion. The strict same helper/caller transformation also succeeds against retained pre-fix70 audit sources; `prior-audit/native.patch` and candidate files show the independent source delta. The retained old glue still uses `to_animation_value_iter`, unlike fix 70. The current patch changes neither glue nor value.rs. This establishes source-level independence, **not an executed pre-fix70 browser/build result**. Root must still check application on the chosen standalone Git base. Keep the animation diagnostic outside the standalone WPT unless root separately validates that base.

## Prior art, tests and remaining gates

Bug 1858848 implemented computing initial values at collection time, explicitly preserving the specified `CSSPropertyRule` initial text. Its full retrieved Bugzilla record is retained. Bug 1864736 concerns the computed-value representation; bug 1883255 concerns broader animation/dependency behavior. This audit makes no novelty claim or exhaustive duplicate search. The helper defect is narrower than same-effect animation dependency ordering.

Existing tests retained here cover typed default initial values, normal computation, CSS-wide attr substitution and ordinary variable CSS-wide fallback. Their checked metadata paths have no files; that is only a metadata observation, not evidence of execution. The six-case probe supplies both actual helper callers and controls distinguishing ordinary typed parsing and preseeded noninherited defaulting.

Recommended root gates: the six-case paired WPT; existing `registered-property-initial.html`, `registered-property-computation.html`, `attr-css-wide-keywords.html`, `wide-keyword-fallback-001.html` and `wide-keyword-fallback-002.html`; existing registration/CSSPropertyRule tests to preserve descriptor serialization. The keyframe diagnostic can be rerun on the current stack as supplemental evidence. Actual Rust compilation, formatting/lint, base application, dynamic registration/viewport behavior and runtime regressions remain outside this source-only proposal.

No Lean or universal native proof is claimed. A useful future contract is that explicit initial-defaulting copies the same selected computed provider entry as ordinary initial seeding, preserving the full value and bucket while leaving descriptor storage untouched; cache freshness and registration selection must be proved or admitted separately.
