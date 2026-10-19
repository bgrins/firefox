# Next formal component: declaration planner/executor

## Independent specification

Use a finite ordered list of typed declarations: identity, value, importance; the identity has optional logical group and mapping kind. Define CSSOM set constraints independently: exactly one target, requested value/priority, unrelated declarations retained, target after opposite-kind same-group members. A deterministic reference setter may use the specification's remove/append-or-in-place example. Define parsing insertion separately, with existing-important precedence. Define removal by filtering the selected longhand/custom or shorthand identity set.

## Representation and providers

Model the native declaration vector, importance-bit vector and identity set, proving at each public boundary: lengths match; identity set equals vector projection; vector identities are unique. Value equality is an admitted equivalence and must agree with native PartialEq on probed values. Property identity, logical-group membership and mapping kind come from the actual generated property metadata. All expansion is a finite, stable, unique provider list excluding direction/unicode-bidi/custom; preserve the content-pref filter and actual CSS-wide/WithVariables iterator. Unknown absolute canonical order is a parameter, not a hardcoded normative physical-first rule.

## Required theorems

1. Full per-declaration planner soundness: None iff reference state is unchanged; Append, UpdateInPlace and AppendAndRemove execute to a state satisfying set constraints. Equal values with later opposite-mapping members still reorder. Importance changes are independent of parsing precedence.
2. Normal batched executor: source unique and same mapping kind per logical group; original positions unique; descending removals and ascending rank fixups reach the sequential reference, preserving aligned importance and set coherence. Prove bounds and subtraction safety, plus exact order of unrelated entries. Do not assume fabricated mixed-kind input satisfies this theorem.
3. All sequential executor: arbitrary mixed groups, ordinary/custom destination entries, sparse and complete initial destinations, all CSS-wide/WithVariables payloads, both priorities. Prove sequence refinement and relative-order convergence for opposing identities under any fixed canonical expansion order.
4. All preparation gate: initial `any(non-None)` equals existence of a changing step in sequential execution, using the first-change argument. A full all state can still need reordering. Distinguish step-changed flags from final serialized-text equality; MutationObserver behavior needs the real serializer/outer update semantics or an explicit separate boundary.
5. Parsing push/extend and longhand/shorthand removal preserve representation, with exact priority and excluded-property behavior. Drain completion, fresh plans, stable callbacks and no mid-operation mutation are explicit native premises.
6. Arbitrary finite operation sequences compose only after the concrete state-dependent transition and provider readiness conditions are proved. Independent action lists from the preceding publication model do not supply this theorem.

## Native bridge

Extract complete planner/executor/removal and actual set/identity/importance providers, including all iterator and ordinary generated subproperty lists. Include actual CSSOM and declaration-list caller policy differences. Test concrete opposing-order cases, unchanged values with reorder, important-to-normal changes, mixed append/update/remove positions and all exclusions. Compile semantic mutants for omitted ordering, wrong importance, ascending removal, missing rank correction, and omitted set removal, each with a concrete successful witness and corresponding kernel counterexample. Do not claim compiler correctness or full rendering/serialization without those providers.

## Current boundary

No Lean model or compiled native harness is implemented in this static audit. The browser discrepancy is established for root's diagnostic inputs. Exact canonical expansion order is still a specification gap; the proposed universal relation quantifies over any fixed order. Independent review must adjudicate that relational interpretation before native repair acceptance.
