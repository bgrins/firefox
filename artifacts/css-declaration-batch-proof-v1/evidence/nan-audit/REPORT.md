# CSSOM NaN equality audit

## Result

No conformance bug established by this lead. The proposed observation—an extra style mutation after repeating an identical NaN-containing value—is allowed by CSSOM's change-flag contract. No browser, native executable, build, or Git operation was run. This is a bounded source/spec audit, not a formal verifier result.

There is a real model-admission issue: arbitrary `PropertyDeclaration::PartialEq` cannot unconditionally be represented by Lean `DecidableEq`. Some specified numeric wrappers retain IEEE NaN and use derived floating equality. This does not invalidate conditional proofs or the finite u16 harness; it prevents extending them to every native value without a comparator contract.

## Exact source chain

The complete files under source/ are copied from the current workspace and pinned in SOURCE-PINS.json; no historical revision identity is asserted.

* `properties.mako.rs`, generated `PropertyDeclaration::eq`: same variant dispatches to the payload's equality.
* `specified/number.rs`, `NoCalcNumber::eq`: explicitly recognizes two NaNs as equal. Plain `opacity:calc(NaN)` is therefore a negative control, not evidence of the suspected nonreflexivity.
* `specified/time.rs`, `NoCalcTime`: raw `CSSFloat` plus unit, derived PartialEq. `Time` delegates through `NumericUnion` to boxed `CalcNumeric` for math functions. `Time::parse_with_clamping_mode` calls `CalcNode::parse_time`; `into_time` simplifies and retains the node.
* `specified/calc.rs`: NaN identifier produces `NoCalcNumber(NaN)`. `Leaf::try_product_in_place` multiplies a unit leaf by the number, using `Leaf::map`; the time branch constructs `NoCalcTime::from_seconds` without NaN normalization. `Leaf::simplify` canonicalizes its time unit without censoring NaN. The generic product simplifier merges the leaves and retains the resulting dimensional leaf. `CalcNumeric`, `Leaf`, and `GenericCalcNode` derive PartialEq. `NumericUnion::eq` compares unpacked values.
* Consequently `animation-delay:calc(NaN * 1s)` is a concrete source-derived candidate for a nonreflexive specified value. This is an inference from the full source path, not an executed parser observation. `calc(infinity - infinity)` can produce the same numeric condition; it was not independently traced as a second case. `NoCalcAngle` and `NoCalcLength` also derive raw-float equality; this audit does not claim exhaustive property reachability for them.
* `declaration_block.rs`, `declaration_update`: an existing nonlogical declaration with unequal payload selects UpdateInPlace rather than None. The ordinary prepare/update pipeline therefore can publish again. Logical-group ordering has its independent preceding check and is not altered by this finding.
* `geckolib/glue.rs`, `set_property_to_declarations`: prepare's false skips the before-change callback and update; true invokes the callback, drains the scratch declarations into update, and returns true.
* `nsDOMCSSDeclaration::ModifyDeclaration` calls SetCSSDeclaration only on true. `nsDOMCSSAttrDeclaration::SetCSSDeclaration` routes to the element. `nsStyledElement::SetInlineStyleDeclaration` passes the declaration block directly into SetAttrAndNotify; it does not serialize and reparse to canonicalize it. Its before-change closure notifies observers. `Element::SetAttrAndNotify` stores the attribute, queues applicable custom-element callbacks and notifies attribute observers without a same-serialization guard in this body.

## Optional diagnostic, not a failing WPT oracle

If an implementation observation is useful, use a fresh div per pair. Set animation-delay to `calc(NaN * 1s)`, record specified serialization and computed value, start an attributes MutationObserver, repeat the identical setter, and inspect takeRecords(). Compare `1s`, `calc(0 * 1s)`, and `opacity:calc(NaN)` controls. Require each initial parse to produce a nonempty declaration. Record serialization, length, priority and records separately. A positive record count is permitted; do not assert zero or file a correctness defect from it. No performance claim follows without measurement.

## Useful formal correction

Parameterize native planning by a comparison predicate rather than replace it with mathematical equality. For no-op safety require only that a true comparison plus equal importance permits preserving the old declaration (under the chosen semantic/serialization relation). Permit false negatives and conservative UpdateInPlace. Prove first-changing-step/all gating using determinism and that None preserves the state; neither needs universal reflexivity. If an idempotent implementation/no-publication theorem is desired, state the stronger reflexive admitted-domain hypothesis separately and prove that admission for each native value family. A u16 harness cannot discharge this condition for floats. Equality of serialization alone must not become the general semantic premise.

## Coverage and remaining boundaries

Retained complete supplied files and read the relevant definitions and call bodies, not the entire generated property universe. Number, time, angle and length wrappers were inspected; only the time parse/product path was traced in detail. Percentage, resolution, colors, random functions, computed style difference, and animation restart behavior are not covered. No all-CSS, all-PartialEq, parser, compiler, allocator or DOM lifecycle proof is claimed. No native patch or conformance WPT is recommended for this lead. Reopen only with an independently specified forbidden observable effect or a measured optimization goal.

The checker authenticates the capsule and verifies selected source anchors; it is not a native execution or proof checker.
