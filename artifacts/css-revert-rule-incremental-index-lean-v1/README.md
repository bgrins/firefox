# Incremental source index and prefix gate

This proof extends the exact `IndexedExclusions.lean` dependency, without copying or modifying its definitions. It models the frozen incremental candidate with cascade source hash `d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1`. `SOURCE-MAPPING.json` pins the candidate and records the native/model correspondence. No native source, earlier proof, canonical library or Git index was changed.

## Derived invariants

`Cursor` contains an ordered remaining node list, a list representing visited-block membership, and the partial owner map. Nodes are optional blocks, so source-less rule-tree nodes are represented explicitly. `visit` skips an already visited block and otherwise inserts every original entry in that block using the old proof's `insertEntries`. `scan` checks the cached query first and advances only until the query is indexed or the suffix is exhausted. It does not assume that lookup succeeds.

| Result | What is proved |
| --- | --- |
| `scan_spec` | The resulting map has exactly the visited blocks' entries; total source support is preserved; the queried owner is sound and complete for the original support; the remaining cursor is an exact suffix. |
| `scan_visited_projection`, `partial_domain_is_visited_prefix` | A consumed prefix is exhibited, not assumed. The map's exact domain is the old visited blocks plus blocks in that consumed prefix. Untouched source suffixes are not silently pre-indexed. |
| `lookup_matches_full_index`, `covered_lookup_succeeds` | A partial lookup returns the same optional owner as the old eager index. Coverage plus unique ownership implies success, including queries requiring further enumeration. |
| `sequential_invariant`, `after_history_covered_lookup` | An arbitrary finite query history retains the valid partial index, total source support and suffix cursor. A subsequently covered query still succeeds. |
| `cached_query_does_not_advance`, `lookup_preserves_cached` | An indexed query leaves the entire state unchanged; later scans preserve earlier cached owners. Revisited blocks need no new source traversal. |
| `scan_miss_exhausts` | An absent result implies that the remaining source cursor is empty. The model does not invent an early failure. |
| `prefix_fold_projection`, `prefix_is_exact_projection` | Folding prefix insertions over the same successful full-key history produces exactly the projection of the full exclusion set. Duplicate insertions are allowed. |
| `absent_prefix_avoids_lookup` | Missing prefixes return false and preserve the whole cursor without any coverage premise. |
| `prefix_gate_equivalence`, `complete_gate_equivalence` | Prefix-filtered incremental rejection equals the old cold list predicate and its full inclusion/fast-bit/cumulative-cutoff gate. Coverage is required only when the prefix is present. |

Two compiled finite examples supplement the general theorems. The first query indexes a block's sibling entry and stops before an untouched suffix. A later history revisits an earlier block, crosses a duplicate and a source-less node, reaches the last block, and then queries the exhausted cursor. A covered cache hit still succeeds; an uncovered query returns `none` in the model. The native implementation panics on that uncovered query: the example does not claim that execution continues after a native panic.

The eager comparison uses remaining blocks plus visited blocks as its source roster. This rearrangement preserves support; the reused `source_roster_support_suffices` theorem makes owner lookup insensitive to that rearrangement under unique ownership. Source order is not being discarded from CSS cascade evaluation.

## Native boundary

Original-entry and block identities are abstract types. `UniqueOwner entries` is reused unchanged: one live original declaration identity belongs to only one block. The fixed `entries` function supplies stable block contents throughout one invocation. Repeated occurrences of the *same* block are permitted. The key remains physical longhand plus full normalized priority plus block identity; prefix projection drops only the block component. Equality retains flags, context/origin and layer, rather than using the ordering projection.

Native applicability depends on the earlier ownership/provider audit: original entries remain live and unmoved under guards; both ordinary/prioritary consumers and direct-block input enumerate originals covered by their retained source view; substitution does not replace the owner-query address with an owned temporary. A finite, stable parent-chain roster and the correspondence between its source-less nodes and model `none` nodes are refinement premises. This is not a Rust provenance, borrow checker, allocator or FFI proof.

The native map/set operations must obey their key equality, insert, membership and get contracts. Functional maps and boolean sets model those operations; hash tables themselves are not verified. Block insertion and successful exclusion insertion are modeled at their completed boundaries. Allocation failure or panic does not produce a continuing partially committed state. In native `insert`, owner resolution completes before either prefix/full-key set changes; both folds therefore describe the same successful insertion history. No independent, possibly stale prefix set is assumed correct.

Coverage is needed for insertions and for identity checks whose prefix exists. The no-prefix theorem genuinely requires none: it proves the old cold exclusion list cannot reject that query, regardless of its owner. When the prefix exists, the success theorem discharges the native owner lookup obligation from coverage; it does not hide `.expect`/panic behind an assumed successful lookup. The mathematical query-history function is total even for uncovered entries; native histories correspond to its successful, covered owner calls. Prefix-skipped checks contribute no owner call and leave state unchanged.

The model checks its cache again after source-less and duplicate nodes; native code continues directly on those branches. Those branches do not change the owner map, and their entering query was a miss, so this extra pure check changes no result or state. The model makes no claim about equal instruction counts.

The proof does not equate semantic CSS rule occurrences with shared allocations, prove substitution observation equivalence, or establish CSS conformance. Those remain the separate occurrence quotient/audit and fixture obligations. No new browser bug or candidate adoption is claimed.

## Cost and replay

Cursor advancement consumes source prefixes without rewinding, and each newly visited block contributes its full entries once. With ordinary expected hash-table costs, the source argument remains O(S_p + D_p + Q) over a successful history, plus exclusion storage, where S_p/D_p are visited nodes/distinct-block entries and Q counts checks/insertions. Hash collisions, allocation costs and constants are outside this proof. A deep first query or a huge requested block can still be expensive; no timing improvement follows from the theorem.

Run `python3 artifacts/css-revert-rule-incremental-index-lean-v1/replay.py` from the repository root. The replay pins the entire existing import closure, uses the bundled Lean 4.35.0-rc4 compiler, retains command/results and removes its temporary compilation directory. `VALIDATION.json` records the final actual invocation and axiom audit. Development logs are explicitly earlier attempts, not validation of the final source. No native build or browser run forms part of this artifact.
