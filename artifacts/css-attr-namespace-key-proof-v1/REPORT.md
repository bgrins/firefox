# Qualified attribute key components

## Verdict

**Mathematical components proved; native/provider/substitution admission remains open.**

This package adds 42 theorems and preserves 11 earlier observer/namespace-boundary theorems. The source-only replay builds eight modules including Audit, checks all 53 theorem axiom lists, and rejects two namespace-erasing semantic mutants. It is a reusable proof component for the chosen repair, not a complete proof of CSS substitution or the native Tarjan traversal.

The original name-only counterexample is retained verbatim in AttributeNamespaceBoundary. A further graph counterexample proves that erasing namespace identity can turn one directed edge between distinct qualified attributes into a self-edge. The earlier browser reproduction and signed postguard package remain unchanged.

## Model and useful results

A key contains a local-name token and a resolved namespace token. Namespace token 0 denotes the null namespace in the dispatch examples; `none` denotes an unresolved namespace and is not token 0. Tokens abstract actual resolved name/URI identity, not prefix spelling or pointer addresses. Values are arbitrary.

The attribute map distinguishes absent entries from explicit invalid entries (`Option (Option Value)`). Preload records a qualified key as seen even when the provider fails, and populates the map only on success. Subsequent preload of that exact key is deduplicated. Stores and invalidations may follow in any order.

| Component | Proved result |
|---|---|
| QualifiedKeys | Different namespaces give different keys; writes to distinct keys commute; invalidation preserves a different namespace; unknown and known-null resolution remain distinct |
| QualifiedHistories | Exact-key preload deduplication; both distinct-namespace values survive; arbitrary preload/store/invalidate histories preserve every untouched qualified key |
| NamespaceBuckets | Namespace→local-name buckets flatten exactly to qualified maps; bucket seen insertion agrees with qualified seen membership; arbitrary bucket histories simulate qualified histories, yielding nonclobber directly |
| GraphIdentity | Custom, attribute and non-custom nodes are disjoint; attribute node equality retains namespace; every injective encoding preserves and reflects arbitrary reachability and SCC membership; component invalidation affects exactly its attribute members and is idempotent |
| ResolvedDispatch | The native `(name, Option<namespace>)` API is an injective encoding of custom vs qualified-attribute targets; null attributes remain distinct from custom properties; unresolved namespaces create no primary and route to the supplied fallback; URI-equal prefix aliases give identical plans |

The SCC theorems are about graph identity and paths. They deliberately do not assert that distinct namespace nodes can never be in the same SCC: genuine cross-namespace dependency edges can form a cycle, and then invalidating both is correct. The preserved false-self-edge counterexample isolates identity loss from real cyclicity.

## Native binding

The complete formatted candidate-v2 files are retained and authenticated against the root manifest:

- custom_properties.rs: `4c6bbf3ced241a0df98f90011871a4810d6306f7740e8c10411547b80e1ec92d`
- properties/cascade.rs: `be204d2bbdef0ec5130139eaeb56adf8fb869d09565f9b7b4c70e5ad3f61d425`

Candidate-v1 and its formatting-only differences to v2 are retained. The original complete source snapshots and counterexamples are separate. SOURCE-ADMISSION.md maps actual functions and representation changes to the component theorems and names remaining obligations. Inspection of these sources binds the intended model operations; no Rust-to-Lean verified translation is claimed. Native compilation/browser acceptance belongs to root and is not inferred from these proofs.

## Explicit exclusions

1. Correct parsing of namespace prefixes and atom/Namespace URI equality, Hash/Eq coherence, and collection implementation behavior are external representation premises.
2. The graph's actual used edges, fallback selection, registered/non-custom dependencies, traversal order, lowlinks, stack handling, numeric index bounds, and SCC completeness remain unproved. The injective graph theorem must not be instantiated with native numeric indexes until their allocation invariant is justified.
3. `planAttribute` models the unknown-namespace branch after native `can_chain` admission. The pre-existing untyped-reference early exit is not admitted by that theorem. Nested parsing still carries the existing bug 2021110 limitation; this component does not claim all namespaced chained references work.
4. Invalidation here means `remove_attr`/SCC computed-map invalidation. DOM attribute mutation and all style invalidation machinery are outside this component.
5. The full evaluator, CSS-wide keyword/rollback interaction, cache/value determinism, context evolution, memory/ABI/performance, and complete original C1–C13 scope remain open. A namespace representation proof does not close those obligations.

## Replay

Authenticate FREEZE.json and replay.py first. Run `python3 replay.py` for integrity, or:

```
python3 replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean --output /new/output-directory
```

The executable SHA is checked. All Lean source is copied into a fresh temporary directory and compiled there without pre-existing project oleans. Audit rejects proof shortcuts and unexpected axioms. Two mutants erase namespace comparison from bucket writes or SCC invalidation; both must fail their theorems. `work/` is development output only and excluded from the sealed source closure. No native, WPT, Git, browser or build changes were made by this agent.
