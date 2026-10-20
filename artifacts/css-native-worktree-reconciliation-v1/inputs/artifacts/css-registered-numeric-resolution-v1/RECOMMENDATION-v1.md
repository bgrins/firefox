# Registered numeric dependency fix: concrete completion plan

## Recommendation

Proceed with the six numeric syntax capability fix and the existing 76-case acyclic regression, accompanied by narrowly enumerated expectation updates for the unchanged tentative test. This is a reviewable partial implementation improvement; it does not need to wait for a complete solution to Houdini issue1080. Keep the 30 font-consumer outcome changes visible in the patch description and metadata rationale. Do not describe them as 30 fixed tests or as proven conformant cycle handling.

This review recommends the plan; it does not claim the remaining metadata validation or reviewer approval has already happened. No native, WPT, metadata, build, or commit operation was performed here.

## What is established

The exact baseline/patched comparison in `direct-substitution-comparison-v1.json` covers all 76 new subtests:

| Route | Before | After | Count |
|---|---|---|---:|
| Direct relative numeric operands | FAIL | PASS | 24 |
| Direct absolute numeric operands | PASS | PASS | 12 |
| Substituted numeric operands | PASS | PASS | 36 |
| Registered length controls | PASS | PASS | 4 |

Thus the patch makes direct acyclic numeric values agree with an already-working substitution route. This is evidence about scheduling and expression spelling, not a proof that all cyclic or font-consuming direct/var pairs agree. The saved eight-case true-cycle probe separately demonstrates a preexisting direct/var difference; it has no normative assertions and cannot settle issue1080.

The source reason is precise: syntax capability permits inspection of actual recorded unit references. It does not give every number a font dependency. Plain numbers and absolute inputs retain empty actual font references. The helper has both eager and traversal callers; changing only one fast path is insufficient. A helper-local six-type list would have the same graph consequences. Separating scheduling from cycle edges requires a larger design and is unnecessary to fix the settled acyclic defect.

## Primary trace and scope of uncertainty

For a registered numeric value, [Properties API computed-value behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) delegates numeric functions to their defined computation. [Values4 computed math](https://drafts.csswg.org/css-values-4/#calc-computed-value) resolves contextual operands, while [font-relative units](https://drafts.csswg.org/css-values-4/#font-relative-lengths) normally use the element's font. [Registered substitution](https://drafts.css-houdini.org/css-properties-values-api-1/#substitution) supplies the computed typed value to consumers. For fixed own font-size/line-height and width-only consumption, the own-element oracle is **REACHED**.

The parent-font exception concerns units used in a font-affecting property's value. It does not prescribe recomputing one registered property's typed value in whichever consumer happens to reference it. The tentative registered tests assert the custom value itself equals parent metrics, before checking the font consumer. A failure at that first assertion says nothing about whether the later consumer assertion would pass after changing the expected custom value.

[CSSWG issue8169](https://github.com/w3c/csswg-drafts/issues/8169#issuecomment-1632890687) resolved direct font-property context and explicitly left typed custom-property interaction for further work. [Houdini issue1080](https://github.com/w3c/css-houdini-drafts/issues/1080) is still OPEN in the freshly retrieved API snapshot. Its first proposal removes the output-length restriction; later comments also identify missing font-weight dependencies for metric units. Neither that open discussion nor the test establishes a normative requirement to retain the old accidental eager parent-context result.

For the six fixed-em registered cases, font-size remains 10px and the consumer does not set font-size. Own-em follows the typed-value computation chain without the ex/cap/ch/ic feedback question. A focused own-em test correction is supported. For the 24 metric-unit cases, this review remains **INCONCLUSIVE** about a universal final cycle/metric oracle. Expected-failure bookkeeping must preserve that distinction. It does not certify the new metric values.

## Test history matters

Local immutable Git history records introduction of the tentative test with computed-time math support in commit `ead20ee980471940ab583fa927b5cf1546f6e6b3` (bug2040168, D300978, 2026-05-25). The broad parent expectation was introduced there alongside 55 expected failures. It was not a later resolution of issue1080. The same-day follow-up `4f3792c37af679cc9853c508fbe2b0538c0055a4` (D302369) added integer rounding to the registered font-consumer loop, but left the no-consumer loop without rounding. Both exact test/history patches are retained here. Commit review provenance is useful evidence; it does not itself resolve the missing spec rule.

## Recommended minimal landing patch

1. Retain the already-tested six-type capability change and all 76 new acyclic assertions. No new expected failures belong to the new regression.
2. Remove exactly the 18 now-obsolete expected-FAIL entries for the existing acyclic subtests. Do not change their assertion or rename them.
3. Add exactly 30 expected-FAIL entries for the changed registered font-consumer assertions, leaving their source intact for this patch. Identify the six fixed-em cases separately from the 24 unresolved metric-feedback cases in the review note. Link issue1080 and the typed-substitution rationale adjacent to the metadata grouping; do not use a generic 'regression' or 'flaky' label. This records a known failure of an unsettled assertion rather than asserting that any arbitrary regression is acceptable.
4. Preserve every other existing expectation. In particular, keep the two acyclic integer ex/cap failures pending the focused rounding correction below. Do not mark the whole file expected FAIL, skip it, add PASS-or-FAIL alternatives, or remove the direct-property controls.
5. Scope platform conditions to evidence. The capture is macOS/aarch64; it alone does not justify assuming every platform's font-dependent assertions have identical outcomes. Use the project's existing metadata convention and actual available CI/platform results. Where outcomes differ, retain exact conditional entries rather than weakening assertions.
6. Run the same four-file WPT gate after those precise metadata edits. Require 76/76 new PASS, all harnesses OK, no unexplained status changes, and only the explicitly retained known failures. The existing exit1 capture remains immutable evidence of what changed; a metadata-clean rerun is the outstanding completion gate, not a new semantic experiment.

This path is justified because it fixes a settled oracle, corrects a concrete capability abstraction, preserves already-working equivalent acyclic expressions, and openly tracks the uncertain collateral assertions. It would not be justified if a direct-property normative control regressed, if a custom value began using parent metrics in the new acyclic tests, or if broader unrelated failures were swept into the metadata. None of those is shown by the retained 48-transition evidence.

## Separate focused test correction

A small follow-up can correct the no-consumer integer expected value with the existing `numericType.round` mechanism. [Values4 numeric functions](https://drafts.csswg.org/css-values-4/#numeric-functions) require integer conversion at the consuming integer position: about4.5333→5 and6.6167→7. The earlier follow-up already uses this treatment in the other loop. Remove those two expected failures only after that corrected test passes.

A second isolated correction may split the six registered-em cases from the broad parent-metric loop, assert own10 in the custom value and valid consumer, retain direct font-property parent30 controls, and check both direct and unregistered-input-var spellings. It should also confirm the child's font-size remains10. These are concrete finite follow-ups, not a requirement to resolve all metric cycles before landing the capability fix. Do not rewrite the other24 to observed values or select a cycle default without a resolved oracle.

## Limits of approval

I support the minimal landing plan above with explicit per-case metadata and recorded unresolved scope. I do not approve a blanket claim of no possible cyclic behavior regression, all-platform expectations inferred from one capture, or a final normative value for the24 metric-feedback assertions. Root still owns implementation, review and commit. This report does not file or modify any external issue.
