# Substituted inherit dependency flag: independent source review

## Recommendation

The proposed narrow repair is supported by the source and specification. No source blocker found. Recommend integration and paired browser validation; this capsule does **not** accept an unexecuted candidate or prove the invalidation scheduler. The confirmed baseline defect is stale registered reset-property inheritance after a parent value change.

Reviewed native patch SHA256 `14b9a124fcd9a670f3ee2968735395ed89c2f22212c709802f465ce60a346801`. Its entire effect is one import and an OR of `INHERITS_RESET_STYLE` before the selected parent lookup, under `!registration.inherits()` in the nonroot inheritance arm. No value, taint, cache, namespace, declaration priority, or map update code changes.

## Independent normative and browser oracle

Current CSS Values 5 Appendix A, Resolving in Properties, requires a substituted sole CSS-wide keyword to act as that keyword. Cascade 5 Explicit Inheritance copies the parent's computed value even for a property whose default inheritance behavior is false. Unset on that reset property uses its initial value. See SPEC-TRACE.md. These rules apply to the current computed value, not a one-time snapshot.

The six retained tests independently establish initial child values, mutate the parent, establish its new computed value, then read the child. Both substituted-inherit cases reach the final assertion and retain 10px instead of 20px. Direct inherit and substituted unset controls pass, both with and without a padding mutation. Cleanup returns undefined via Element.remove(). There is no transition, animation, timing wait, font, layout geometry or rounding dependency. Raw reconstruction gives 2 FAIL, 4 PASS, one harness OK and suite end. RUN.json records stable before/after pins, including the exact probe and original custom_properties source; those binary hashes are retained evidence, not independently reproduced executions.

Only the project build containing repairs 71/72 has browser evidence here. No candidate runtime, release-browser, or isolated-upstream runtime claim is made.

## Complete source path and exact correction

1. `cascade_custom_property` selects declarations and stores unresolved custom values; its immediate no-reference path and both graph resolution paths invoke `substitute_references_if_needed_and_apply`. The latter only handles successful substitutions here. Attr-store operations have a non-None namespace and bypass the `is_var` CSS-wide block.
2. The complete helper parses the resulting CSS-wide keyword and matches `(keyword, registration.inherits(), context.is_root_element())`. The modified arm contains nonroot inherit for either registration kind, plus unset/revert variants only when inherits=true. Consequently its added `!inherits()` guard is true **only** for nonroot reset-property Inherit. The explicit revert TODO is unaffected.
3. The bit is set before either parent-map result: Some clones the parent value; None removes the child entry. Both create a dependency on later parent changes. Moving the flag into Some alone would miss absent-to-present changes. Parent GIV and typed initial interpretation are unchanged.
4. `StyleBuilder::add_flags` uses shared `Cell` mutation and bitwise OR; existing flags are retained. `build` publishes the builder flags. `INHERITS_RESET_STYLE` is not an inherited or maybe-inherited flag: a child does not acquire an unrelated ancestor's explicit dependency. Normal cascade rebuilds the local bit from its actual declarations.
5. `Gecko_CalcStyleDifference` derives reset-only from equality of inherited ordinary style structs. `GeckoRestyleDamage::compute_style_difference` clears reset-only if inherited custom maps differ, but preserves it for non-inherited custom-map-only changes. Thus an otherwise identical parent can trigger reset-only even without the padding mutation. This closes the discovery note's previously open reset-only provider step.
6. `accumulate_damage_for` in matching.rs derives child hints. Reset-only changes normally produce `RECASCADE_SELF_IF_INHERIT_RESET_STYLE`; structural exceptions use unconditional recascade. `needs_to_recascade_self` in data.rs consumes that conditional hint by checking the child's stored flag. Both ordinary and animation-only restyle-kind selection consult it. The missing bit explains the two failures without asserting whole scheduler correctness.
7. Direct explicit reset inherit already adds the same bit in `cascade_custom_property`. This patch brings the substituted path's dependency recording into agreement; it does not alter the direct path.

## Root, pseudo, lifecycle, and caller boundaries

`apply_declarations` defines root as `pseudo.is_none() && element.is_root()`. The root inherit case takes the separate initial arm and cannot gain this new bit. A pseudo on the document element is not misclassified as the root. The retained eager-pseudo resolver supplies the originating primary style as parent and the pseudo argument explicitly. The common helper therefore uses the intended parent and records reset inheritance when reached. This is a source path review, not a runtime proof for every pseudo kind, shadow tree, lazy/anonymous pseudo, or animation traversal.

No new allocation, ownership transfer or mutable map borrow is introduced by the flag OR. The inherited map reference and Cell flag operation use existing shared-access APIs. Rust compilation remains a root gate. The patch does not itself address registration cache freshness or all rule-cache reuse paths. Those are existing provider admissions, not inferred closed from the flag change. Source snapshots of provider files are retained independently of the original browser's limited source pins.

## Standalone and prior repair independence

The exact patch applies with zero fuzz and reverses byte-for-byte on both the retained original project source and the root-supplied upstream Git blob `976279105b2e78b8666a959eb3f25c9176cefaf8a:servo/components/style/custom_properties.rs`. The current-base result must exactly equal the complete proposed candidate. Upstream's surrounding helper has earlier kind/attr-store APIs, but the complete selected inheritance arm is the same. Both add_flags and the ComputedValueFlags import route already exist independently.

Repair 71 changes how the separate initial-value arm obtains its value; this witness copies an explicit parent 10px/20px value and uses a literal 1px initial control. Repair 72 changes direct inherit's early optimization and missing-parent update in cascade.rs; this witness's substituted path does not use either changed site, and its direct control has a present parent. Neither prior repair is a semantic prerequisite for this correction. Patch applicability is source evidence; no upstream native build or browser execution occurred in this review.

## Cost, useful final controls, and remaining gates

The branch adds a boolean test on the already selected uncommon CSS-wide inheritance path and a flag OR. Necessary recascades may increase work for styles that really inherit reset properties; no performance benchmark or asymptotic whole-tree guarantee is claimed. No changes affect ordinary non-CSS-wide substitution, normal inherited properties, root inheritance, unset-reset, failure handling, or attr-map publication.

Recommend keeping the compact six-case core and adding a universal reset absent→present→absent sequence, an inherited-property control and root/pseudo controls if root's final suite allows them. None is claimed executed here. Final acceptance still needs root's exact formatted source identity, compile, paired final WPT/regression evidence, lint, and minimal final native+WPT patch packaging. This is a source-discovered and browser-reproduced invalidation bug; the existing explicit-inherit Lean model did not prove or discover this scheduler defect, and no new universal theorem is claimed here.

## Final proposed seven-case WPT

Reviewed root test SHA256 `d87eaf487e9f41a98efd00a9c72cbe3f1ab6b813e4022b0d9ecb08afa541711f`, retained as evidence/final-test.html. The six original tests are unchanged. The seventh registers universal/reset syntax with an explicit initial token and repeatedly sets the parent to missing-var, present-token, missing-var. It checks the parent at each step and then checks both the child's custom-property serialization and an unregistered var() consumer's fallback. Universal registered invalid substitution produces GIV rather than the typed-registration unset behavior; cloning/removing the actual parent Option is therefore the correct oracle. This directly exercises both None and Some flag-admission paths. Cleanup returns undefined. No new issue found in this proposed test. Its paired runtime is still a separate root gate, and is not inferred from the original six-case raw log.
