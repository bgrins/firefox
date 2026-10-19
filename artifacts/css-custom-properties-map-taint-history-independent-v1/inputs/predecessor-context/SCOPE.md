# Exact contract and admissions

## Proved

1. metadataSame true implies equality of optional payload-plus-taint values under PayloadSound; taint equality is derived.
2. The shared/unique scalar map update equals unconditional replacement for every optional old/new value. Removal remains absent without payload soundness.
3. The two-stage repaired pipeline equals its resolver under PayloadSound, ReferenceFreeProvider and EligibleDomain. When the early gate is ineligible, the resolver may be arbitrary and no reference-free premise is needed.
4. Arbitrary finite histories and every prefix preserve the same selected-value/URL observation under those per-operation premises.
5. For a valid query contained in a fully tainted region, the source-shaped overlap observer projects to the scalar URL observer. Exact state equality also preserves that range observer.

## Native admissions, deliberately open

- PayloadSound is a semantic quotient contract. Native Value<Component>::PartialEq omits attr_tainted and url_data; VariableValue::PartialEq compares CSS text. The model adds taint explicitly. It does not establish that ignored URL data or other metadata are irrelevant to every observer. Do not instantiate payload equality as equality of the entire native struct.
- Incoming.eligible is a supplied label. In native code it depends on the declaration kind, old value's as_universal(), and reaching the comparison after earlier guards. History instantiation requires correct labels relative to the evolving actual state. The fixed modeled resolver must represent the appropriate contextual computation for every admitted input. This is not a theorem for every native declaration history.
- The native universal equality branch has no reference guard. EligibleDomain requires eligible inputs to be reference-free. ReferenceFreeProvider requires their result to be their declared payload with syntaxAttr OR explicitAttr. A concrete source subdomain is the universal, is_var, no-references direct-constructor branch. Deriving this domain for every native gate comparison is open. unresolved_domain_necessary demonstrates why dropping it is unsound in the model; it does not establish reachable native misuse.
- Unique/shared scalar updates abstract Arc ownership, nearest-owner lookup, COW insertion, counting and iteration. Their complete native refinement is not proved here.
- observeURL abstracts one selected URL parse under a fixed environment, with the queried URL inside a fully tainted substitution. parse is arbitrary and shared on both sides. Actual serialization, equivalent token sequence, byte positions, range placement, selected substitution, parser errors, resource resolution and URL data are external. Native range comparison uses inclusive boundary tests; the model matches these comparisons and does not adjudicate empty/boundary-range semantics.
- Provider side effects, attribute reads, reference graph/SCC bookkeeping, dependency and cache flags, registration routing, lifecycle, global CSSOM semantics, memory/overflow/compiler behavior and the browser pipeline remain open.

The narrow no-reference universal constructor supports an admission; binding its source does not prove upstream parser invariants or the full substitution/provider relation. Every theorem remains valid on its stated mathematical inputs even where native admission is unproved.
