# Lazy owner index and rule exclusions: alternative C candidate

This is a reviewable alternative to the repeated scans in frozen `css-revert-rule-cold-membership-diagnostic-v1`. It is **not adopted, compiled as Gecko, or measured**. `native.patch` changes only `servo/components/style/properties/cascade.rs` and applies after that exact cold-C candidate, which in turn requires coherent A+B+D. The cold candidate's `stylist.rs` direct-block argument and A+B+D's `applicable_declarations.rs` remain prerequisites. Their hashes and the exact overlay preimage are in `SOURCE-ROLES.json`; this package copies only the changed native file.

## Representation and behavior

`Cascade::rule_exclusions` becomes `Option<Box<RuleExclusions>>`. Both constructors initialize it to `None`. The only construction site is the already-admitted Rule arm after the existing seen, inclusion, cumulative cutoff and identity guards, substitution and color handling. A cascade without an admitted Rule allocates none of this box, owner index, block-deduplication set or exclusion set. No field is added to the per-declaration record or inline declaration buffer.

On first construction, `DeclarationSources::index` walks the current Rules source chain or direct Block source. It enumerates each distinct block allocation once and maps each original declaration's address to a borrowed reference to its block. The temporary block-address set is discarded after construction. Subsequent checks recover the owner with an address lookup and test a hash set keyed by physical longhand, full normalized `CascadePriority`, and block address. Both repeated source searches and the growing exclusion-vector scan are removed.

`RuleExclusionKey` derives `Eq`, `PartialEq` and `Hash`; priority normalization uses the existing `unimportant()` and retains flags, context/origin and layer. It does not use priority ordering equivalence. Block pointers are hash/equality keys only; this change adds no raw-pointer dereference or unsafe block. The index values and source view retain borrowed block lifetimes. `original_declaration` remains the lookup input after substitution; replacements and cache-produced values are not indexed as source identities.

The fast membership bit and A+B+D cutoff guard stay in their existing order. Non-Rule rollback updates the same cutoff state. Rule inserts the identity exclusion without erasing cutoffs. Physical mapping, its writing-mode observation, dependency discovery, both longhand dispatchers, custom-property processing, visited construction and the direct source view remain as in cold C. Multiple insertions of the same identity collapse to set membership, whose boolean semantics match the previous vector's `any` predicate.

## Ownership and equivalence boundary

The source audit in `css-rollback-c-ownership-audit-v1` supports the required original-entry → unique live block-allocation relation: nonempty cloned/serialized declaration arrays are distinct, guarded entries stay stable, and current iterator/direct callers use the covered originals. The representation proof in `css-rollback-c-membership-bridge-lean-v1` provides the corrected bit/map/exclusion invariant and membership-based gate interface. Neither artifact formally verifies this new Rust hash-map implementation.

Indexing reads the whole source view once, including blocks after the first trigger; normal declaration collection has already visited that source view. A post-Rule lookup of an uncovered original now fails at `RuleExclusions::key`, including an otherwise non-Rule candidate. Current audited callers cover these entries; this preserves an explicit producer contract rather than inventing provenance. A future arbitrary iterator passed with a mismatched source view would violate it. As before, the semantic rule-occurrence versus shared-allocation quotient and nonduplicate cascade observations require their separate arguments.

## Cost and next validation

For S source nodes, D entries across distinct source blocks, E cutoff-admitted identity checks and R Rule insertions, expected hash-table work is O(S+D+E+R). Permanent auxiliary storage is O(D+R); the temporary deduplication set is O(distinct blocks). This is expected hash-table complexity, not a worst-case bound. Indexing includes entries for other properties/custom declarations, so a single Rule in a large source tree can allocate considerably more than the cold vector. Small-count performance and memory may regress; no size or speed improvement is claimed.

Actual check `3a4aa2`, exit 0, verified Servo-configured rustfmt, zero-fuzz forward/reverse patch application with exact bytes, and unchanged declaration/cutoff/custom/dispatcher regions. Run `python3 artifacts/css-revert-rule-lazy-index-candidate-v1/check.py` to repeat those source checks. `CHECK.log` retains commands. **Rustfmt parsing/formatting is not Rust typechecking:** borrow inference, crate traits and target integration still require the root-owned native build.

After compilation, use the existing C72/D64/substitution20 and direct-block coverage, preserving the A+B+D controls. The existing cold-cost workload can compare the original cold candidate and this alternative at matching source/build/settings, with native coverage counters if needed. No browser, WPT, benchmark, build, live-source, Git, old-artifact or canonical Lean mutation was performed here.
