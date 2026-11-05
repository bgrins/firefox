# Trial1: deduplicate source blocks through the owner map

Separate, unadopted candidate based on exact incremental cascade.rs d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1. Candidate cascade.rs is cac13ba7ff2bbdfd54b906d7854a8ba703c2b013770ed4d121eb6b16af1bed6e. The patch changes only DeclarationSourceIndex: remove its persistent block HashSet and initialization, then use the first original entry's owner-map membership as the nonempty-block deduplication test. No other optimization is included. C stylist.rs and A+B+D applicable_declarations.rs remain exact unchanged prerequisites pinned by SOURCE-ROLES.json.

The source cursor still advances before examining a block. A block with no declarations immediately continues; it cannot contain the requested original and contributes nothing to the owner map. For a nonempty block, an already-mapped first original entry skips reinsertion. Otherwise the same reserve, complete entry insertion and post-insertion query check run. Prefix gating, full (physical property, normalized full priority, block) equality, all callers, substitution identity and the rest of cascade.rs are byte unchanged. No raw pointer dereference, per-declaration field or common-path allocation is added.

## Representation premise

The owner map contains complete visited blocks' entries after every continuing operation. Under stable block contents and the existing unique-owner condition, membership of a nonempty block's first entry is equivalent to that block having been completely indexed. If it is present, it cannot originate in a different block; if the block was indexed, all entries including the first are present. Duplicate source occurrences and queries for later sibling entries remain supported. Empty blocks need no stored visited identity; consuming one changes the cursor but not the observable owner map.

This uses the same live original-entry/owner identity relation as the existing incremental proof, not a new pointer-sharing claim. A failed allocation/panic during insertion is not treated as a continuing partially committed state. A separate Lean refinement is being prepared using the existing visited-prefix/whole-block/unique-owner invariants; no proof result is claimed by this package.

## Intended cost difference and limits

The separate visited-block table, its growth and drop disappear. Duplicate-block checks become reads from the owner map, which can be larger than the removed set; performance can therefore improve or worsen. The owners/prefixes/full-exclusion tables and lazy box remain. All original declaration entries in every visited distinct block are still indexed, including unrelated custom declarations. Dense chains still consume most relevant source blocks; no reduction in necessary source traversal or dense benchmark ratio is promised.

Expected traversal/lookup complexity remains O(S_p+D_p+Q); stored visited identities are now derived instead of occupying an additional table. Empty-block identities are not retained. Exact allocation counts, byte sizes and speed are unmeasured. This trial deliberately does not combine admission-key reuse, post-insertion-query elimination, eager indexing, small-list thresholds or grouped exclusion sets, so its eventual comparison isolates one representation change.

## Checks and next gates

Actual source check910c49 exited0: Servo-configured rustfmt, exact d329 preimage, zero-fuzz forward/reverse patch application with byte equality, and exact preservation of the whole file outside DeclarationSourceIndex. CHECK.json and logs retain the results; temporary copies were removed. Rustfmt is parsing/formatting, not native typechecking or Gecko compilation. No live source/index/history, native build, browser or timing action occurred.

Before any adoption, finish representation refinement, root-owned native compilation and the same190+controls+occurrence correctness boundary. Include empty/repeated blocks and later-entry queries in refinement examples, and preserve all:revert-rule/many-prefix coverage in broader evaluation. Then compare uninstrumented d329 and this single-change candidate using the existing dense/single/no-Rule workloads and fresh bracketing baseline evidence. Any diagnostic allocation/counter instrumentation remains separate from production and timing runs.
