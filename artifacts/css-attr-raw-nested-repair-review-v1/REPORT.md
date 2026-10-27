# Raw nested attribute repair review

The proposed native change matches the branch ordering in the pinned CSS Values 5 Editor's Draft of 27 October 2026. I found no semantic blocker in the proposed distinction or its two explicit existing-test oracle corrections. This is a static review, not acceptance of a built fix.

## Specification route and changed oracles

The complete captured attribute-replacement algorithm returns present bare/raw-string text as one string before invoking typed attribute substitution. Successful primitive number/unit parsing likewise returns before that recursive route. Only typed attribute contents invoke generic substitution with an attribute context. Missing or invalid primaries instead substitute their selected fallback. The parent being an attribute does not alter those branches. [Attribute replacement](https://drafts.csswg.org/css-values-5/#attr-substitution)

The earlier attr-cycle case enters typed contexts for data-foo and data-bar, then performs a raw read of data-foo. That read returns the original data-foo text as one string. Its expected value is therefore `"attr(data-bar type(*))"`, not a cycle-invalid property. The later case reads both active attributes in raw form and returns two strings: `"attr(data-bar type(*), fallback)" "attr(data-foo) attr(data-bar)"`. Neither raw read re-enters an attribute guard; string contents are not reinterpreted as function tokens. These are explicit oracle corrections, not newly passing old expectations.

Actual typed reentry remains a cycle. Attribute-only cycles poison their participating attribute contexts and may allow the outer attr fallback. A used raw/primitive fallback containing var(--x) can instead poison the enclosing property context, whose final guard check rejects an inner fallback rescue. [Generic substitution](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function), [guards](https://drafts.csswg.org/css-values-5/#guarded)

This review manually re-read the relevant captured algorithm and prior positive traces; it makes no exhaustive indexed reachability claim. No fresh spec fetch or new browser experiment was performed.

## Native and test scope

The native delta removes the parent-attribute exception from visit_value_references. All non-type attr references use the existing primary classifier; only an actually selected fallback is traversed, and no raw attribute node is added. Removing the now-unused parent argument and its two call arguments follows directly. Typed traversal, SCC propagation, pending-demand returns and actual replacement/serialization code are unchanged by this delta.

The proposal depends on the non-type-fallback repair-v3 classifier. It is not independently applicable before that prerequisite. That classifier resolves the stored namespace and queries AttributeTracker, treats present raw text as valid even when empty, and shares primitive parsing with actual replacement. A non-type reference without a fallback needs no graph edge; actual substitution still supplies its value and tracking. Runtime tests must establish tracker/cache behavior rather than inferring it from graph omission.

The 29 proposed cases include 26 fixed cases and three mutation callbacks. They cover raw self/chain reads, genuine typed self/mutual cycles, used versus unused raw/primitive fallback, property-context invalidation versus attribute-only fallback, and namespace separation. The existing fixture retains 37 calls with precisely two intended oracle changes. If a mutation callback fails, later states within it cannot be counted as observed. Namespaces, parsing, first-argument substitution, taint and tracker invalidation still need production validation.

## Relationship to Lean

The sealed guard model's raw_nested_literal and raw_nested_guard_trace establish the one-typed-context/literal-raw distinction for normalized expressions. two_raw_attributes_remain_literal establishes the two-string structural case; typed_mutual_marks_only_attribute_cycle and cross_context_all_participants distinguish attribute-only cycles from cycles that include a property. present_raw_ignores_cyclic_fallback and valid_primitive_no_cycle establish branch exclusion, while invalid_primitive_self_invalid preserves genuine used-fallback cycles. These are useful semantic checks on this proposal.

They are not Rust refinement theorems. The model receives normalized expressions, primitive parse results and coherent identities; it does not implement CSS tokenization, DOM namespaces, registration, dynamic first arguments, taint, cache reuse or mutation tracking. Its property and attribute numeric key tags are distinct, but that fact is not a proof of DOM namespace handling. No new proof, accepted bug or normative coverage credit is claimed.

Candidate build and browser comparison remain necessary. Keep both corrected old expectations visible in the comparison assessment, require genuine typed/property-cycle controls to remain correct, and do not treat old baseline attr-cycle PASS as evidence against the current algorithm.
