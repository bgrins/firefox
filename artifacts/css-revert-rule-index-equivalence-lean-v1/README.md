# Cold-list / indexed exclusion equivalence

`IndexedExclusions.lean` proves the owner-lookup and exclusion-predicate interface between frozen cold C and the lazy indexed alternative. It derives the index from source-entry lists, rather than assuming that the completed index returns the correct owner. This adds no browser bug or native adoption claim. Neither candidate, earlier proof library, live source nor Git state was modified.

## Proven interface

| Obligation | Result |
| --- | --- |
| Per-block entry insertion | `insert_entries_lookup`: after inserting the actual entry list, a query maps to that block exactly when it is an entry; other mappings are retained. |
| Exact index domain and owner | `build_index_correct`, `fresh_index_correct`: the deduplicating source walk maps a query to a block iff that block occurs in the source roster and contains the query. |
| Cold search versus index | `indexed_owner_matches_first_search`: index lookup equals the original first-containing-block search, including `none` for absent entries. |
| Successful native lookup | `covered_lookup_total`: a source-covered original entry necessarily has a successful index lookup. |
| Repeated source blocks | `source_roster_support_suffices`: duplicates and ordering of source-block occurrences do not change the owner lookup when block contents are stable and ownership is unique. |
| List insertion versus exclusion set | `set_fold_membership`, `built_set_membership`: after any finite insertion history, set membership equals membership in the list, including duplicates. |
| Physical property, priority and owner matching | `cold_exclusion_is_key_membership`: the original three-part scan predicate is exactly full-key membership for a covered original entry. |
| Final rejection gate | `indexed_exclusion_matches_cold`, `full_guard_equivalence`: indexed and list-based rejection agree, including their combination with inclusion, fast-bit and cumulative cutoff predicates. |
| Identity components are retained | `key_retains_flags`, `key_retains_physical_property`: changing flags or physical property cannot be erased by the key construction. |

The key is `(physical longhand, full normalized Priority, block allocation identity)`. It uses structural equality, not scalar cutoff ordering. Normalization clears importance in the existing priority model while retaining flags, context/origin and layer. Owner discovery returns a block only; the key still uses the triggering event's priority. Both insertion keys and later rejection predicates therefore agree at this model boundary. Existing cumulative-cutoff and corrected C fast-bit proofs remain separate reusable results.

The proof uses explicit finite folds and a first-match scan. An index is represented by a function from original-entry identities to optional block identities; set storage is represented by a boolean membership function. This is a model of insert/lookup behavior, **not** an extraction or verification of Rust `HashMap`/`HashSet` internals. Native hash tables must satisfy their ordinary key-equality and insert/get/membership contracts.

## Ownership, guards and provider assumptions

`UniqueOwner entries` requires that a live original declaration entry belongs to only one block identity. `entries : block → List declaration` fixes each block's contents for the invocation. The source roster may repeat the same block arbitrarily. There is no assumption that rule-tree nodes themselves are unique, and no theorem equating a block allocation with a semantic CSS rule occurrence.

The pointer interpretation depends on live, unmoved original entries and borrowed block lifetimes under the source/guard contracts. `css-rollback-c-ownership-audit-v1` supplies the bounded source argument for distinct nonempty cloned/shared-memory arrays, non-zero-sized declarations, active read guards and covered caller references. This Lean proof does not independently verify Rust provenance, allocator disjointness, guard implementation, unsafe/FFI behavior or lifetime enforcement.

Coverage is required for **every declaration reaching an indexed key query**, not merely declarations which themselves resolve to Rule. The native indexed candidate uses `.expect` after its map lookup. In contrast, the old cold guard could scan exclusions and return false for an uncovered non-Rule declaration without performing its asserted owner search. The audited ordinary/prioritary/direct producers supply covered originals, and substitution retains `original_declaration`; a future generic iterator inconsistent with its source view remains an uncovered native edge. The model defines an absent indexed exclusion lookup as false only to make the function total; the final equivalence theorem requires coverage and never licenses the native panic path.

Two compiled countermodels make the premises concrete. If two different blocks share entry identity 0, index construction can choose the later block while cold search chooses the first (`shared_entry_counterexample`). If an entry is absent from the roster, lookup is `none` (`uncovered_entry_is_absent`). Neither is claimed reachable in the audited native callers. They prevent silently dropping ownership or coverage assumptions.

The gate/lookup theorems do not prove whole-browser execution, substitution purity, observation equivalence of repeated semantic rule occurrences, registration/cycle behavior, or CSS conformance. In particular, they do not promote the existing restricted ordered-block quotient to a native global theorem.

## Complexity and validation

The indexed design removes the explicit repeated source and exclusion-vector scans. With S source nodes, D entries across distinct blocks, E eligible checks and R Rule insertions, ordinary hash-table assumptions give expected O(S+D+E+R) work and O(D+R) persistent storage. Adversarial collisions can invalidate that expected bound; no worst-case constant-time hash theorem or timing result is proved. The proof's functional maps also do not model native allocation or hash-table costs. Eagerly indexing all source entries on the first Rule can regress small workloads despite improving long chains.

Actual Lean invocation `f957fd`, session `21540`, terminal `211a5c`, exit 0 compiled the pinned imports and final source with Lean 4.35.0-rc4. Fourteen theorem axiom reports passed with no `sorryAx`, custom axioms or `native_decide`; the new module has no warnings. Existing dependency warnings remain in the log. `RESULT.json`, `VALIDATION.json` and `lean.log` retain command/results; temporary scratch was removed.

Replay from the repository root with `python3 artifacts/css-revert-rule-index-equivalence-lean-v1/replay.py`. `IMPORTS.json` pins the existing dependency closure and `SOURCE-MAPPING.json` pins both native candidates. No native build or benchmark was run for this proof.
