# Query handoff mapping and assumptions

This artifact models the candidate query-only handoff in candidate.patch, pinned
by SOURCE.json. It is an implementation contract, not a derivation of CSS style
query semantics. NATIVE-SOURCES.json preserves the source-review capsule's pinned
baseline identities; the full native source bodies and patch-application evidence
remain in that capsule. Hash authentication is not a native refinement proof.

| Candidate concept | Model |
| --- | --- |
| Query mask intersection | `project` retains separate named and unnamed query bits; font and aggregated other bits are excluded. |
| Animation-only and nonempty guard | `collected`; the declarative supply/mark relations state independent logical conditions. |
| Per-producer queue | Arbitrary finite list of `Producer`, including duplicates. Queue completeness is assumed, not inferred from native execution. |
| Eligible immediate traversal children | `Tree.children`, exact parent correspondence, and `styled`; the boolean summarizes element/data/has_styles eligibility. Non-elements are omitted from the tree's element universe. |
| Insert child hint | `applyDelivery` unions the projected mask with the old hint. |
| Dirty path from producer through selected root | `ancestors`; equivalent to starting at an eligible child's traversal parent. No child or sibling dirty mark is invented by that delivery. |
| One ancestry path per eligible producer | `activeNodes` filters collected producers with at least one eligible child. |
| Dedicated ancestor HashSet | `Certificates.certified`, separate from native dirty state. |
| Stop at certified ancestor | `clippedAncestors`; equivalence requires `CertificateSound`. |
| Rootward prefix marking and insertion | `certify` models the completed batch effect. Actual reverse-insertion steps and Rust container behavior remain native mapping obligations. |

The finite `Tree count` universe is the selected traversal subtree. Every modeled
node therefore has a path to this traversal root, which need not be the original
DOM root. `next_edge` supplies each nonroot parent and `decreases` proves strict
depth descent. These are explicit assumptions; the model neither fabricates a
root-reaching chain for an arbitrary DOM nor permits a producer outside that
subtree. Traversal children/parents, eligibility, identities, and hints are fixed
while a drain is modeled. Worker joining, queued SendElement validity, mutex
behavior, and native memory safety are not proved.

`Supplies` and `Marks` are independent inductive relations, not equalities to the
executables. The exact handoff theorems prove both directions of delivery and
ancestor coverage. The ordinary font replay is outside the model; the query
handoff preserves existing font bits and does not depend on producer font bits.

A sound certificate set is ancestry-closed: every certified node's complete
ancestor chain is certified and dirty. An empty certificate set is sound for
any preexisting dirty bits. `clipped_exact` identifies precisely the uncertified
part of a full path; `certify_sound` preserves the invariant.
`certify_many_equivalent` proves full-path dirty coverage across arbitrary finite
producer sequences. `optimized_handoff_equivalent` connects this optimized
sequence over `activeNodes` to the reference handoff's dirty relation. This
composition is checked, not assumed.

The native code marks then certifies each element in reversed prefix order;
this mapping is consistent with the certificate invariant but is not a proved
refinement of each Rust insertion. No complexity bound, next-traversal selector
matching result, global CSS convergence, animation-drain bound, or memory-safety
claim follows from these finite handoff proofs. One executable case deliberately
supplies an unsound certificate and demonstrates why the premise is necessary.
