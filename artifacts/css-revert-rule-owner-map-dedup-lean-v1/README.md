# Owner-map membership replaces the block set

`OwnerMapDedup.lean` refines the existing incremental index model by removing its visited-block set. It imports the exact prior proof rather than repackaging it. The source mapping pins candidate `cac13ba7ff2bbdfd54b906d7854a8ba703c2b013770ed4d121eb6b16af1bed6e`, based on incremental `d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1`. This is a formal model refinement for an untested native alternative, not a native build, browser validation, performance result or new bug.

For a nonempty block, `first_entry_cached_iff_seen` derives that the first original entry is present in the owner map exactly when the old visited-block set contains that block. Its premises are the existing `UniqueOwner` relation and `IndexFor`: the owner map contains exactly all entries of every visited block. `first_miss_implies_whole_block_absent` derives the complementary fact: if the first entry is absent, every entry of that block is absent. Neither theorem assumes the desired successful lookup.

`visitOwners` implements the candidate's actual choice: skip source-less nodes, skip empty blocks, skip a nonempty block when its first entry is already cached, otherwise insert its entire entry list. `visit_owners_equivalence` proves that this produces the same owner map as the old block-set check. Empty blocks are handled separately; there is no fictitious first-entry address for them.

`erase` removes the old `seen` state. `scan_erasure_equivalence` proves exact equality of the remaining cursor and owner map after a query, and `arbitrary_history_equivalence` extends that equality to every finite query history. This is observational refinement rather than equality of visited-block sets: the old model can record an empty block, while the new model cannot represent that membership and does not need to. Both advance the cursor over repeated empty or source-less nodes. Cached earlier entries remain available after later queries and after source exhaustion, by transfer of the prior incremental theorem.

`owner_lookup_covered` transfers successful lookup from the original source-coverage premise after an arbitrary history. `exclusion_check_refines_incremental` transfers both the boolean answer and erased updated state through the unchanged prefix/full-key gate. `exclusion_answer_matches_cold` then reuses the existing cold-list equivalence, retaining physical-property identity and full normalized priority equality. Coverage is still required when an owner query is performed; a missing prefix avoids it entirely.

The compiled finite example crosses repeated empty blocks, a source-less node and a repeated nonempty block, revisits a cached owner and consumes the suffix. Two countermodels make the assumptions concrete:

* A map containing only a block's first entry causes the new test to skip its unindexed tail. This violates whole-block indexing.
* Two different blocks sharing their first entry can make the second block's novel tail unreachable. This violates unique ownership.

Neither countermodel is asserted reachable in the audited native implementation. Their purpose is to prevent replacing the premises with the weaker claim that “some entry was seen.”

## Native correspondence and limits

The candidate retains its source cursor and owner map, removes the `blocks` field, and reads `declarations().first()` after advancing the source cursor. Its `owners.contains_key(first_address)` corresponds to `Option.isSome`; the ordinary hash-table get/contains contract remains trusted. Whole-block insertion uses the unchanged `insertEntries` model from the original full-index proof. Prefix/full-key sets and callers remain unchanged in the candidate snapshot.

Native pointer identities require stable original declaration addresses, live blocks, guarded immutable contents and the existing producer coverage relation. The finite source roster and actual parent-chain traversal must refine the model's ordered optional blocks. These premises are inherited from the ownership and incremental-index work; this proof does not verify Rust provenance, allocation disjointness, guards, unsafe code or hash-table internals. Insertion is modeled at its completed boundary. An allocation failure or panic is not a continuing partially indexed state.

The model represents an uncovered owner result as `none`; the native function panics. Native execution corresponds to covered successful query histories up to any failure, not arbitrary continuation after a panic. Removing the set can change allocation behavior and instruction count, which are intentionally outside equality of the cursor/owner map. The ordinary hash-cost argument may improve constants and remove one table, but no latency or allocation improvement has been measured here. Semantic CSS rule-occurrence equivalence remains a separate obligation.

## Validation

Actual invocation `5fa3fd`, session `35355`, terminal `e19bd0`, exit 0 compiled the pinned import closure and final module with Lean 4.35.0-rc4. Twelve axiom audits use only `propext` and `Quot.sound`; two concrete examples require no axioms. The new module has no warnings, custom axioms, `sorry` or `native_decide`. Existing dependency warnings remain in the log. The earlier failed development attempt is retained separately.

Replay with `python3 -B artifacts/css-revert-rule-owner-map-dedup-lean-v1/replay.py`. `IMPORTS.json`, `SOURCE-MAPPING.json`, `RESULT.json`, `VALIDATION.json` and `lean.log` retain the exact inputs and result. Temporary compilation output was removed. All work stayed in this new proof artifact; no live source, Git/index, browser/native execution or commit occurred while root owned the diagnostic run.
