# Registered numeric fallback dependency strategy

**Recommendation:** separate dependency admission from raw reference discovery. Preserve the current prototype, but do not use either a registration-type mask or raw substituted token flags as the final authority for font/line-height edges. For the numeric case, first resolve the selected substitution path, validate it against the actual registration, and then derive contextual dependencies from the admitted specified value. Compute/publish that prepared value only after those dependencies are available and cycle handling has completed.

This is an independent design review, not a patch approval or proof. No browser, build, test harness, or native edit was performed here.

## What the existing observations establish

The root's pinned 14-row browser results agree on seven discrepancies: unused em/lh/ex fallback, nested unused em fallback, missing-primary em fallback, wrong-primary/unused-em fallback, and inherited-primary/unused-em fallback. The branch adds `direct-invalid-em`; its run therefore failed calibration. The release run passed calibration. Both retain stable inputs and successful owned-profile cleanup in their receipts. `OBSERVATION-COMPARISON.json` joins the exact rows without converting these observations into acceptance claims.

Three mechanisms must be distinguished:

1. `--ready:5; --n:var(--ready,1em)` admits the numeric token 5. The unused fallback must not be treated as a reached unit conversion.
2. `--n:var(--missing,1em)` substitutes 1em, which fails `<number>` grammar. This must take registered-value invalidation before attempting a numeric value's font conversion. Merely scanning substituted tokens still invents the font edge.
3. `--n:calc(1em / 1px)` can be a valid number while requiring an em-to-px conversion. Its result type does not justify discarding length-operand dependencies.

`--wrong:red; --n:var(--wrong,1em)` is another admission failure: the valid unregistered primary substitutes red. A registration mismatch does not make var() reconsider its fallback.

## Normative boundary

The 9 October 2026 Variables ED selects the fallback only for a guaranteed-invalid primary result. The 27 October 2026 Values 5 ED requires substitution before value transformations/introspection, then parses the resulting property value; a grammar mismatch is invalid at computed-value time. Together these rules support the two admission gates above. [var replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function), [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement), [invalid substitution](https://drafts.csswg.org/css-values-5/#invalid-substitution).

The 6 August 2026 registration ED gives numeric math functions their function-defined computed value. Its explicit relative-unit graph extension still names only length/length-percentage syntax components. This does not establish that numeric math cannot depend on lengths; it leaves the integration of that older graph clause with newer math and guarded substitution insufficiently explicit. [Registered computation](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values), [extra unit edges](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles).

Under the 24 August 2026 Values 4 ED, division inverts the denominator type and multiplies types, so length divided by length has number type. Math computation simplifies with computed-value information, including the em/px ratio; em normally refers to the current element's computed font size. Thus `calc(1em / 1px)` in a registered number really requires font context. [Math typing](https://drafts.csswg.org/css-values-4/#calc-type-checking), [math computation](https://drafts.csswg.org/css-values-4/#calc-computed-value), [font units](https://drafts.csswg.org/css-values-4/#font-relative-lengths).

**Inference, not a separately verified normative cycle oracle:** if font-size also consumes that number, the dependency closes a loop and should not be evaluated with an incidental old/inherited font value. Retaining the dependency is required to compute the noncyclic case correctly. The precise invalidation result for the numeric cycle should be checked against the combined specs and interoperability before a WPT hard-codes it; the registration graph clause does not expressly cover this outer type. This report does not silently extend the earlier length-only rule. Likewise, the original `<length>` unused-fallback question remains separate from the stronger numeric grammar-admission failure.

The current local parser supports numeric calculations carrying `Leaf::Length`; actual support still needs browser calibration with a valid noncyclic computed result, not `CSS.supports('--n', ...)`, which accepts generic custom-property token syntax.

## Concrete implementation boundaries

The captured HEAD/local/upstream code demonstrates why the obvious patches are incomplete:

- `References.flags` aggregates nested fallback flags. `visit_value_references` ORs that aggregate before checking whether a fallback is used; it also ORs flags from a resolved universal provider. `find_non_custom_references`'s initial registration filter is therefore not the sole source of final edges.
- The local `DataType::dependent_types` widens NUMBER/INTEGER/PERCENTAGE/ANGLE/TIME/RESOLUTION to LENGTH. `cascade` uses this before typed parsing, which routes direct 1em into SCC traversal. The static path explains the branch-only invalid-number regression, but is not an isolated before/after proof of causality.
- `resolved_token_dependencies` rebuilds flags from emitted text. That is useful for excluding discarded fallback text, but it does not validate the declared type, distinguish numeric grammar from inert token text, or prove that a discovered operand survives typed parsing/simplification.
- `SpecifiedValue::compute` already calls `SpecifiedValue::parse` before `to_computed_value`. Reuse this boundary rather than creating a second numeric grammar. The parser selects the actual matching syntax alternative and validates entire components/lists. Preserve URL data, namespaces, the actual property ID, and attribute-taint arguments.
- `CalcNumeric` stores a `CalcNode`; its computation maps leaves, and `Leaf::Length` consults the supplied computed context. An admitted numeric value's remaining calc leaves are a concrete place to collect real context requirements. The collector must follow the same value representation and simplifications used for computation.

A bounded implementation direction is:

```text
resolve the primary/provider/attribute path with existing cycle guards
  -> selected token sequence, provenance/taint, and unresolved-demand outcome
handle CSS-wide keywords using the existing registered-property rules
parse that selected sequence using the actual registration
  -> Invalid: apply the existing registered invalid-at-computed-value-time path
  -> Prepared(specified value, provenance/taint, contextual requirements)
visit/demand those contextual requirements
finish SCC / pending-state handling
compute the prepared specified value once and publish once
```

Keep broad `may depend` flags as routing hints if useful, but do not turn them directly into invalidating graph edges. Do not fix the traversal by subtracting fallback bitsets: the same flag can come from both an active token and an inactive fallback, so subtraction loses real dependencies. Separating own/nested flags is useful infrastructure, but still does not solve selected invalid numeric values.

Do not call today's full `substitute_references_with_pending_and_apply` early merely to discover flags: it mutates the result map and computes against possibly unfinished context. Factor a prepare result that can be reused for final application instead. Avoid performing substitution twice; attribute tracking, taint, URL provenance, and other effects must not be duplicated or lost. Pending remains distinct from invalid so a pending primary cannot activate fallback.

SCC handling requires special care. Existing provider traversal must still discover real var/attr cycles even when the surrounding numeric grammar will eventually fail. Do not publish a guessed token sequence when a provider is still an active SCC participant, and do not let an internal fallback rescue a cycle participant. Nor is it safe to skip all later edges just because a node already has a lower lowlink: that can change SCC membership. The prepared-value boundary needs an explicit unresolved/cyclic outcome integrated with the traversal, with final publication deferred until its result is settled. This is the main reason the report proposes a boundary, not an unreviewed drop-in patch.

## Scope and validation before approval

Start with the registered numeric path and preserve the rest of the typed-demand prototype. Do not claim all registered syntax is fixed: unions, multipliers, nested colors/images/transforms, typed attr conversions, percentages, and future dynamic substitution names need their own correspondence review. A union must be classified by its admitted component rather than the union of declared alternatives.

Retain all 14 existing cases. Add the planned rows in `PLANNED-CONTROLS.json`: noncyclic numeric division against a known font, provider-introduced division, genuine dependency-loop observation, unused division fallback, invalid numeric math, and a syntax alternative whose selected ident requires no conversion. Check dependency invalidation after a font change as well as the first computed result. Cases such as `calc(1em / 1em)` require checking parse-time simplification and the spec before deciding whether any context read remains; do not assume either lexical presence or algebraic cancellation is the oracle.

The desired formal extension is an admission-and-evaluation model: substitution emits only the selected branch; grammar rejection precedes contextual computation; successful typed preparation preserves the contextual reads used by evaluation; pending is not invalid; and publication occurs only after genuine dependencies settle. The existing finite-expression completion theorem proves stability under its abstract coherent-completion assumptions. It does not model numeric typing, actual Rust AST traversal, SCC mutation, or the context-conversion bridge, so it cannot certify this proposed fix as-is.
