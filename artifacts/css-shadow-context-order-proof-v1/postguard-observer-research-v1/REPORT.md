# Post-guard observer algebra and a namespace obstruction

## Result and scope

This artifact extends the approved C1–C13 investigation without altering either sealed predecessor package. It supplies 33 kernel-checked component theorems in five modules (plus the Audit module). It does not close native/provider/evaluator admission or the complete cascade proof.

The meaningful observer is the actual style-sharing decision and future source-matched shorthand-cache lookup, together with the two observed monotone flags. Equality of evaluation counts or raw attribute-vector representation is neither asserted nor needed for those consumers. The earlier pre-filter observer counterexample remains intact in its sealed package.

## Native findings

`AttributeTracker::query` appends a namespace on every query. Repeating the same query produces a different SmallVec. `have_same_referenced_attrs` consumes the recorded values solely through nested `all` comparisons of target/candidate attribute reads. With stable providers, support of (local name, namespace) suffices for that consumer. This preserves both namespace identity and missing-attribute observations.

The corrected local shorthand cache retains the `Arc<UnparsedValue>` source. All entries produced by one successful shorthand parse, including physical aliases, are installed after substitution has recorded its attribute queries. The tracker and cache share the lifetime of `apply_declarations`. A ghost query certificate attached to each modeled cache entry is therefore a useful invariant: cache hits need not repeat dependencies already recorded. The certificate is derived for every modeled history starting from empty, rather than assumed independently at every hit.

A CSS-wide keyword returned directly after substitution precedes shorthand parsing and cache fill. Repeating that Rule-path observer leaves the cache unchanged, sets monotone flags, and appends redundant query support. The model proves those observations idempotent and commutative, and congruent under an arbitrary common continuation of cache fills, queries, hits, and Rule observations. Both the sharing predicate and future source-matched cache lookup remain equal after that continuation.

A separate concrete obstruction arose during source admission: the typed-attribute substitution map and seen set erase namespace identity. `AttributeNamespaceBoundary` proves that no map indexed only by local name can represent two different namespace-provider values at that name. The frozen `attr-namespace-probe-v1` supplies eight browser rows, exact source pins, current primary-spec trace and known-prior-art note. Browser/WPT execution is pending in that subpackage; root owns execution and adjudication. This is separate from rollback and cannot be hidden by weakening attribute identity in the observer abstraction.

## What the theorems actually quantify

| Module | Unconditional mathematical component | Native admission still required |
|---|---|---|
| AttributeObservers | Arbitrary attribute histories; query return independent of tracker; consumer depends only on support; concrete vector non-idempotence | Stable ElementContext/TElement reads and this consumer's Boolean interpretation |
| CacheObservers | Arbitrary fills/overwrites/queries/hits from empty preserve prior-query certificates; recorded dependencies make skipped hit queries redundant | Actual parse/substitution branch maps to each operation; cached values remain valid across context evolution |
| RuleObserverAlgebra | Rule-path flags/cache/support observation is idempotent and commutative; sharing and dependency certificates are preserved | Same Rule evaluation yields the supplied query support and flags; no omitted native effect changes the chosen execution |
| ObserverContinuation | Equivalent states remain equivalent after arbitrary common operations; repeated Rule preserves future sharing and source-matched cache lookup | Native operation selection and payloads agree; the theorem does not prove substitution determinism or manufacture a common continuation |
| AttributeNamespaceBoundary | Namespace erasure cannot represent a provider that distinguishes two namespaces at one local name | Browser reachability and actual parsing/provider correspondence for the retained witness |

The ghost cache query field is erased before comparing native cache observations. Keys, values and atom identities are modeled as Nat/String tokens; this does not prove hashing, allocation, lifetime, parser, Arc identity, FFI, or data-race safety. The model does not merge the native small vectors or change any implementation.

## Remaining obligations

C7/C10/C13 still need a source-level relation joining raw collection, rule-source quotient, native evaluator and all post-guard effects. In particular, actual substitutions may choose different branches when the computed context changes. The same-source/normalized-priority quotient theorem cannot be instantiated merely by giving the query-support or common-continuation premise a native-sounding name.

The successful CSS-wide-keyword return branch is bound by source inspection. This package does not prove all generated shorthand parsers incapable of producing a Rule entry through another branch. It does not establish parser purity or all effects of registered value conversion and environment providers. No complete native semantic equivalence is claimed for arbitrary aliases, mutable provider states, or inherited scoped identities.

C11's inherited-owner no-path refutation remains unresolved. Original saturation-only C10/C11/C13 refutations, the original A Layer→Layer counterexample, and the corrected A+B+D then C dependencies remain preserved. The newly isolated attribute hypothesis is not evidence that C's rule exclusion is wrong; it blocks a blanket claim that all native attribute substitution is already admitted to the independent CSS reference.

## Replay and integrity

`python3 replay.py` checks pinned inputs (and FREEZE.json when present). Supply the pinned Lean executable and a new output directory to rebuild every module in a fresh temporary directory:

```
python3 replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean --output /new/replay-output
```

The runner verifies executable SHA, rejects proof shortcuts, compiles only these five source modules plus Audit, audits all 33 theorem dependency lists, and admits only standard kernel axioms propext/Classical.choice/Quot.sound. Actual used lists are retained in replay logs. No old .olean or native build is reused. `work/` is excluded development scratch; all accepted source, native snapshots, source/index differences, the separate frozen probe and final replay evidence are pinned. Native/browser/Git files were not modified.
