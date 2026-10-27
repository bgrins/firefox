# Raw nested attribute: repair scope

Proposal only; no native patch or branch observation yet. The sealed raw-nested audit contains the complete current-spec trace and the conflicting WPT history.

Smallest semantic change: in visit_value_references, do not call visit_link for the contents of an existing bare/raw-string attr(), even when its parent node is VarType::Attr. Reading that primary returns a CSS string before another attribute substitution context is entered. Keep a missing raw attribute's used fallback traversal intact.

Implementation needs an occurrence-specific primary classifier using AttributeData's resolved namespace and AttributeTracker's actual attribute read. Do not infer raw-primary validity from the typed-provider cache: the same attribute may have a typed cyclic occurrence and a raw literal occurrence. A present empty string is a valid raw primary. Preserve the attribute read/invalidation tracking effects.

This can be scoped to the spurious-edge path inside an attribute node; it need not repair skipped fallback edges at ordinary custom-property nodes in the same patch. Prefer sharing primitive classification with substitution rather than independently reimplementing numeric parsing. Any shared helper must be included in the native changes necessary for the owning fix, not an unrelated tooling commit.

Required checks: typed self-bare, explicit raw-string, type(<string>), two-attribute raw nesting; genuine typed cycle; missing raw attribute with a taken typed fallback cycle; existing raw primary with an unused cyclic fallback. The artifact WPT candidate preserves all 13 original probe cases. The existing attr-cycle.html raw-nested row disagrees with current-spec ordering: resolve that oracle explicitly before landing; do not silently change its expectation.

This lead is separate from previous typed-provider preparation (7822bb6) and type()-specific fallback eligibility (e3ba54f). Neither removes the parent-attribute exception in can_chain. No exfiltration or memory-safety claim follows from these observations.
