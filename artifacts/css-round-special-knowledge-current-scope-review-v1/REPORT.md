# Narrow infinite-step guard review

The three-line generic-calc guard plus one WPT page is a plausible standalone repair with accepted125 runtime NaN priority already present. No finite-quotient arithmetic change or broader canonical-value gate is needed for this boundary. Current generic calc, specified calc, number and easing bytes exactly match the v3 source captures (d85f46). This read does not authenticate a new build or authorize execution.

The historical 19 tests have sound oracles: 17 opacity tests exercise an unresolved value becoming infinity or NaN, and two tests preserve context-free repeat admission. At font32, sign(1em - 16px) is positive; multiplication by either infinity leaves an infinite value, so Round with an infinite step yields NaN. At font16 the multiplication itself yields NaN. The surrounding arithmetic must retain NaN until top-level opacity becomes zero. Support, font, input-sign and stable-read assertions prevent unsupported syntax from passing unnoticed.

The guard also changes finite unresolved values. Add four tests, one per strategy, to cover this materially missing scope. Hold calc(0.5 + 0.25 * sign(round(STRATEGY, sign(1em - 16px), infinity))) while changing font8→16→32→8. Expected arrays are nearest/to-zero [.5,.5,.5,.5], up [.5,.5,.75,.5], and down [.25,.5,.5,.25]. Capture all states before assertions and retain font/mixed-sign/literal calibrations. This yields23 targets without duplicating the full224 diagnostic matrix. Fixture authoring is coordinated with root/typed agent; this review does not claim the successor exists or has passed.

The existing37 diagnostic differences contain21 in the value-unknown/infinite-step branch and16 in the intentionally untouched infinite-value/unknown-step branch. Do not report all37 as repaired or make the untouched branch an all-PASS condition. Basis-dependent leaf knowledge and the broader arithmetic/easing deferral work remain separate.

Ordinary repeat stores a contextual Integer and does not require context-free resolve at admission. Preserve the corrected five-case policy outcomes true/true/true/true/false; do not restore the old mistaken rejection oracle. The old audit's subgrid-rejection statement is historical: accepted127 changed that branch. Current easing has accepted143's both-endpoint protection; steps, cubic-bezier and linear still use context-free scalar gates. The inspected mixed-unit trees fail those gates before and after this guard, but that is bounded reasoning, not universal admission equivalence. Retain existing repeat/integer/easing regressions, the corrected five policy controls, and accepted143's six safety cases in the paired roster. Actual paired results and complete signatures remain required.

## Existing proof reuse

CssSemantics.ImplementationSupport.RoundSpecialKnowledge.unresolved_value_no_constant proves that upward rounding of an unknown finite-sign value with infinite step cannot be replaced by one result valid for both signs. This directly supports preserving missing classification information, rather than interpreting a nonleaf negative predicate as false knowledge. nan_priority supplies the class-level requirement met by accepted125 after deferral. infinite_value_retained_iff and unresolved_step_no_constant explain the separate untouched dual branch; they are not evidence that this patch repairs it.

These four laws already transferred from css-round-special-knowledge-audit-v1 into the canonical library. The model assumes resolved class interpretation, omits finite magnitudes and does not prove AST reachability, syntactic-leaf sufficiency, parser admission, IEEE conversion or Rust refinement. No new Lean model, theorem credit or normative coverage increment is needed. This review read the existing statements; it did not replay the kernel.

## Primary specification

Fresh CSS Values4 review confirms that two infinite operands produce NaN; finite values with infinite step depend on strategy and sign. NaN propagates through intermediate calculations and is censored at the top-level boundary. Simplification requires enough information to compute the operation. These support the scoped oracle and retention decision, not universal sufficiency of a syntactic leaf test.

- https://drafts.csswg.org/css-values-4/#round-infinities
- https://drafts.csswg.org/css-values-4/#calc-type-checking
- https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree

No browser, native build, source edit, index operation or canonical state publication occurred. This is review of a known open boundary, not new discovery or acceptance.
