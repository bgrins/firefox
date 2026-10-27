# Guard-model correspondence and boundary

The existing css-attribute-guard-cycle-model-v1 models active contexts, cycle poisoning and opaque raw tokens. Its root replay reports 36 audited declarations (13 general laws, 23 closed examples), nine decisive false controls and only standard Lean axioms. This proposal does not change or rerun that model and earns no additional formal coverage.

| Model result | Intended native correspondence |
|---|---|
| present_raw_is_literal | A present raw primary supplies no attribute-content graph edge, regardless of the caller node kind. |
| valid_primitive_ignores_expression | A valid numeric/unit primary has no nested expression dependency. |
| missing_raw_uses_fallback / invalid_primitive_uses_fallback | The occurrence-specific helper selects fallback.references when the primitive/raw primary fails. |
| two_raw_attributes_remain_literal / raw_nested_guard_trace | Typed guards are retained, while the final raw reads create no repeated context. |
| typed_mutual_marks_only_attribute_cycle | Actual typed cycles still reach SCC traversal; an independent outer property may select its own fallback. |
| cross_context_all_participants / independent_consumer_can_fallback | A used fallback reaching the active property invalidates it, while an independent consumer may fall back. |
| eager_raw_changes_result | The faulty raw-recursion policy captures the semantic direction of the parent-Attr exception being removed. |

The model does not prove native SCC equivalence, actual token parsing, namespace identity, CSS serialization, registration, taint, attribute tracking, cache invalidation or pending-provider semantics. Namespace and mutation cases here are proposed browser coverage for some of those boundaries. The earlier three-context one-string oracle is traced manually; no new Lean theorem is claimed for it.

The change deliberately reuses the used-fallback classifier and its AttributeTracker reads. It neither alters the number-token primitive nor introduces a new interpretation of raw attribute strings. The general native traversal's handling of ordering/short-circuiting beyond these scenarios remains outside this proposal's proof claim.
