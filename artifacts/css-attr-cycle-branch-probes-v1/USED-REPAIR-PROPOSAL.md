# Used bare/unit fallback: repair scope

Proposal only; no native patch or branch observation yet. The sealed used-fallback audit contains the positive specification trace, release observations and exact prior-fix comparisons.

Smallest semantic change: before visit_value_references skips a non-type attr() at an ordinary custom-property node, classify that occurrence's primary. Follow fallback.references exactly when the primary fails. The direct raw/unit read itself creates no attribute-content dependency edge.

The classifier must use the resolved namespace and the actual attribute value through AttributeTracker. For bare/raw syntax, an existing attribute (including empty text) succeeds. For number/unit syntax, use the same number-token/exhaustion test as substitute_one_reference, including whitespace and invalid-token handling. Missing attributes, unresolved namespaces and failed numeric parses select a supplied fallback. No fallback means no fallback edges. Do not use type() provider-map membership as a raw/unit validity test.

Push the selected fallback's References into the existing traversal, so var self/mutual references update the current SCC and invalidate all participants. Do not merely change the recursive seen-name fallback behavior: that could disturb ordinary noncyclic fallback substitution without constructing the missing dependency edges. Do not flatten all fallback references eagerly: existing valid-primary controls depend on ignoring unused fallbacks.

A first patch can scope this to the existing !can_chain branch and retain the separate nested raw-attribute behavior pending its oracle adjudication. The artifact WPT covers the seven release failures and six controls. Mutual variants assert both --x and --y are invalid, and the consumer is green. Preserve typed fallback preparation, occurrence-specific typed eligibility, namespaces and hash-order regression coverage.

This is outside 7822bb6's provider preload and e3ba54f's is_attr_with_type() primary-eligibility check. Both prior native and WPT patches are pinned in the original audit. A release failure alone earns no new branch-fix credit.
