# Draft reading notes

No producer code executed; awaiting immutable source closure.

1. `metadata_same_sound` assumes only comparator true implies abstract payload equality. There is no reflexivity, symmetry or transitivity hypothesis. Nonreflexive native float comparisons may merely prevent skips. This does not establish native payload quotient fidelity: `Value::eq` excludes URL data and taint, and `VariableValue::eq` is CSS text only. A source interpretation of abstract P must be explicit.
2. Corrected map logic preserves None versus a present empty payload, and skips the comparator on unique ownership. The two-stage witnesses correctly show that either old shortcut can mask the other repair.
3. `Incoming.eligible` is supplied while native eligibility depends on old value kind and declaration kind. Source correspondence must name that per-step admission. The native shortcut precedes has_references computation and has no reference-free guard. `EligibleDomain` plus `ReferenceFreeProvider` restricts the theorem, not the production implementation.
4. Incoming taint models syntax ATTR bit OR explicit-taint bit; existing comparison must use outer computed wrapper metadata, not the inner resolved token flag. Draft field names are appropriate, but all Boolean combinations are abstract and need not be source-reachable.
5. `observeURL` assumes a payload parser; `observeAt` uses inclusive overlap matching the actual retained AttrTaint predicate despite the native range documentation calling its end exclusive. The containment theorem is not a proof of full substitution offset production or parser range correctness. Keep both as source admissions.
6. `history_correct` is a semantic update fold conditional on the provider/eligibility and comparator premises. It does not model all map-chain allocation, registered routing, declaration cascade ordering or URL resolution metadata.
