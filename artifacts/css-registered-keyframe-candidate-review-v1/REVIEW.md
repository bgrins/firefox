# Independent registered-keyframe candidate review

## Verdict and scope

Source and WPT review: **acceptable for the bounded repair; no new blocking defect found**. Runtime disposition is recorded separately in RUNTIME.md. This review is of the exact final candidate, not a universal animation/cascade proof or an isolated upstream build. Root retains final acceptance and commit ownership. Another reviewer owns standalone applicability.

The final glue, value and WPT hashes are respectively `94d5ea189192d43b7e11f5046d9ba520134024750618050acd32baf2ff9419fb`, `da158dfacfa2b59c3589cb0d8c06c8b7c2ddb40307674c02e5ec8d66069f6350`, and `7fc360adf2f7faa775f09722f32995911f7ed990c28a79b31b7b36552922370e`. The retained patch is `f4c710b6d4880a9cbfd02c4e420c395e87766983b87e093037a862d799c099f7`.

## Source findings

1. **Actual cause and selected path.** `Servo_GetComputedKeyframeValues` already constructs and resolves a fresh keyframe custom-property map using the target and a real attribute tracker. The old output conversion reparses original tokens for registered custom values and can fall back to Universal rather than produce a typed number. The candidate consumes the computed map only for `CustomDeclarationValue::Unparsed` with a non-universal registration. It avoids a second raw parse on precisely that branch.
2. **Registration and map ownership.** The lookup uses the same document stylist as the builder. `ComputedCustomProperties::get(registration, name)` chooses the registration's inherited or non-inherited map; it does not use the ambiguous inherited-first CSSOM accessor. `CustomAnimatedValue::from_computed` clones both name and optional computed value, including the existing value representation and taint fields. Its body is unchanged; only visibility and documentation change. No borrowed map reference escapes.
3. **Iteration and exclusions.** The replaced `AnimationValueIterator` and the new normal iterator use the same declaration/importance stream, skip important entries and preserve order. For all non-intercepted declarations, `AnimationValue::from_declaration` receives the same mutable context, style, defaults and fresh dummy tracker, and None results are skipped. CSS-wide, Parsed, universal/unregistered and noncustom declarations remain on this path. Generic conversion's other callers are untouched.
4. **CSS-wide exclusion is necessary.** The custom-property builder is seeded from base style; its normal cascade optimizations may skip explicit initial/unset/inherit declarations. Reading that seeded map for every custom declaration would regress explicit defaults. This candidate excludes those declarations, and the WPT distinguishes parent 30, initial 0 and base 42. Existing revert/revert-layer/revert-rule behavior is unchanged and not certified.
5. **Missing values and neutral values differ.** A missing computed custom payload is wrapped as `Some(AnimationValue::Custom(name, None))`; a null declaration block still produces the existing neutral absent animation pointer. The candidate does not confuse guaranteed-invalid custom payload with a missing keyframe endpoint. It uses the existing conversion/serialization semantics for that wrapper.
6. **Caller processing remains intact.** Each keyframe seeds a fresh map; the priority iterator still resets after preprocessing. Simulation failure, pseudo restrictions, animatable/logical assertions, display pref, seen-ID deduplication, output ordering and Arc ownership are unchanged. No new ordering, graph traversal or mutable registration update is introduced by the changed branch.

## WPT review

Six tests isolate numeric interpolation through literal, attr at either endpoint, missing-attr fallback, var and calc. Ten more distinguish CSS-wide and invalid-value endpoints for inherited/non-inherited registrations. `SPEC-TRACE.md` derives the values independently. Pausing and setting currentTime avoids elapsed-wall-clock assertions; computed-style reads flush the effect. Two numeric controls detect unsupported registration/interpolation. Cleanup cancels effects and removes their elements. No network, font, rendering geometry or random input enters the oracle. The stylesheet registrations intentionally persist for the file. Exact integer serialization is appropriate for these values.

## Preserved limits

- The builder/cascade/substitution implementation is a source dependency, not proved correct by this review. Current provider snapshots and static diagnosis are retained. This patch does not make the keyframe hack a complete regular cascade.
- Cross-property keyframe references to skipped CSS-wide declarations and fallback-produced CSS-wide values remain separate static leads; they are not newly solved or hidden by this acceptance. Dynamic dependency/registration updates, all syntax classes, graph cycles and cross-platform runs are not covered by sixteen tests.
- Universal custom-property substitution and generic `AnimationValue::from_declaration` limitations remain unchanged. The adjacent expected failure must remain reported.
- The prior identity capsule establishes conditional ID/readiness facts; it does not establish numeric payload correctness for this repair. No new Lean theorem is asserted here.
- No performance neutrality claim, no isolated upstream runtime claim, no browser test executed by this reviewer, and no whole-provider or universal native correspondence claim.

## Reproduction of the review evidence

Run `python3 -I -S check.py` from any copy of this directory. It authenticates the closed local inventory and exact candidate/original/test pins and checks retained runtime observations. This is an integrity/receipt check, not a browser rerun. No live source tree is required. Review source copies and patch are immutable inputs; the checker does not execute their code.
