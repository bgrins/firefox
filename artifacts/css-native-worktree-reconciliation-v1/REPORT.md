# Native working-tree reconciliation

## Result

All **21 tracked native paths** in the captured diff have concrete pending-repair lineage. I found **no unexplained native hunk, accidental formatter-only native residue, or already-committed accepted repair merely left dirty**. This is a provenance assessment, not renewed correctness or landing acceptance. Preserve the changes.

The audit starts at `8af5b5566fcd1ea7563fca6e22105d586b92520d`. Root concurrently committed the standalone-whitespace index (`e372e7e21cdf`); all 21 captured native files remained byte-identical. Every retained HEAD snapshot was checked against the initial commit. `properties/mod.rs` has no remaining diff. Five changed Python files in `css-shorthand-cache-proof-v1` are recorded but outside this native audit; their lineage/readiness is not inferred here.

## Classification and next gates

| Pending unit | Native paths | Existing evidence and remaining action |
|---|---|---|
| Initial view-transition types | Document.cpp | Independent native review accepted; complete atom-list/type-observation formal companion and review. |
| Contained quote append | nsQuoteList.cpp/.h | 64 new cases pass; independent scope-dirtiness review and formal companion pending. |
| Percentage shape-margin | BlockReflowState.cpp, nsBlockFrame.cpp, nsFloatManager.cpp/.h | Independent native review accepted; provider/recovery, ownership and arithmetic formal scope pending. |
| Collapsed flex alignment | nsFlexContainerFrame.cpp | 150 paired +240 added controls pass; independent strut/spacing review and formal scope pending. |
| Sticky H1/H2 | StickyScrollContainer.cpp | Both independent native reviews and four-variant matrix accepted; full ten-obligation formal scope pending. H3 remains excluded. |
| Language, hyphen ownership, nowrap publication | nsLineBreaker.cpp/.h, nsTextFrame.cpp | Three intentional repairs. Language/hyphen native review accepted; nowrap native gates complete. Full provider/continuation/publication proofs and required independent reviews remain; do not hide refuted partition obligations. |
| Shadow order | level.rs, rule_collector.rs, applicable_declarations.rs, cbindgen.toml | Native gates complete; bounded representation/overflow and full source-admission scope remain. Separate sparse-owner defects are not repaired here. |
| Rollback A+B+D, then rule exclusion C | applicable_declarations.rs, cascade.rs, stylist.rs | Coherent stack validated; component proofs and bounded native reviews exist. Full C1–C13/source quotient/observer closure remains open. Never land historical A v1. C retains memory/performance limits and follows A+B+D. |
| Page selector name | page_rule.rs, stylist.rs | 18 paired print checks and six existing checks pass; independent bucket/specificity review and formal scope pending. |
| Registered numeric relative operands | syntax/data_type.rs | Exact historical candidate hash; 24/76 baseline failures repaired. Resolution recommendation still requires explicit tentative font-consumer/metadata adjudication. No cycle-resolution claim. |
| Backslash-newline fix86 | custom_properties.rs | Exact current root candidate; finish its current source/proof/runtime/packaging acceptance. No other custom_properties.rs delta remains. |

`CLASSIFICATION.json` supplies per-unit patch paths, hashes, concrete next actions and status limits. Historical ledger timestamps/counts are not treated as current aggregate counts.

## Exact correspondence and integration adaptations

The in-memory reverse-context audit matches **82 of 91 native patch hunks** and reconstructs HEAD exactly for **17 complete native files**. It never writes production files. Its nine nonmatching contexts are retained openly, not counted as successful application:

- Sticky H1/H2 overlap in raw patch context. The complete live file equals the retained, matrix-tested `variant-combined.cpp` byte for byte (`fe79e921...`). The prior root review explicitly records this context overlap and commuting changed blocks.
- Three line-break context failures result from composing language and hyphenation additions. The complete current nsLineBreaker.cpp equals the nowrap repair's retained combined candidate (`d9e5f7e0...`); its header and nsTextFrame changes have independent exact reverse matches. The residual diff is an audit intermediate, not a proposed native state.
- Two C import contexts predate committed `Namespace` (3aa7d25635ff) and `PropertyIdRef` (e3ba54f6f826). Current imports retain those names while adding `PropertyDeclarationBlock` and `FxHashSet`. This is an intentional integration adaptation, including import wrapping/order; all substantive C/A+B+D hunks reverse exactly.
- The fourth residual file, numeric data_type.rs, has no standalone patch in that old fix folder. Its complete hash is exactly the recorded tested candidate `b2faa46e...`; the full residual is the six-type capability change plus its related comments/formatting.

The shape-margin indentation and nsTextFrame restructuring match historical patch bytes. There is no evidence to classify them as newly accidental formatting. `PATCH-CORRESPONDENCE.json`, retained residuals, original patch inputs and complete source snapshots make these distinctions inspectable. Existing root receipts establish historical status; this audit does not re-run their browser or proof gates.

## Best next candidates after fix86

1. **Initial view-transition type deduplication:** independent native review and a minimal two-file patch already exist. Its remaining bounded list/atom-provider proof and observation review are substantially smaller than the cascade pipeline.
2. **Sticky auto-inset H1:** strong independent oracle/native review and exact four-way independence evidence already exist. Complete the promised formal contract, retaining the negative-zero correction.
3. **Sticky writing-mode H2:** reuse the same accepted matrix and explicit mapping contract after H1's proof infrastructure, while retaining independent landing and mixed-mode limits.

These are priorities, **not ready-to-commit approvals**. Shape-margin is a reasonable later candidate, with a larger provider/recovery obligation. Page-name matching is small in source but still lacks its independent native review. The cascade, language/hyphenation and registered-numeric candidates carry broader unresolved admissions or normative questions and should not be promoted solely because their finite runs passed.

No native edits, index mutations, builds, browsers, new testing, or removals were performed. Only owned audit artifacts were written.
