# C delivery and prerequisite review

Recommend a separate C production commit **explicitly depending on #163**, `e63fc6b1892bc13f4d0f6583e4efc4b58d1e54db` (Preserve cumulative cascade rollback exclusions). It can be reviewed/landed after that prerequisite, but the retained exact patch is not independently cherry-pickable onto the pre-project baseline. Keep supporting research/proofs/runners in a preceding artifact-only commit. No history, index, production source or native build was changed by this review.

## Concrete minimal delivery

`C-after-163-proposed.patch` contains exactly two Rust files and three WPT changes:

* `servo/components/style/properties/cascade.rs`: exact incremental candidate d32913bd… (source cursor, prefix gate and full-key exclusions plus the existing C source-view wiring).
* `servo/components/style/stylist.rs`: exact C fd5ded7d… caller wiring for the direct declaration-block path.
* Add `css/css-cascade/revert-rule-logical-physical-same-rule.html` (C72).
* Add `css/css-cascade/revert-rule-substitution-source.html` (20).
* Extend existing `css/css-cascade/revert-layer-preserves-inline-exclusion.html` from D48 to D64 (16 extra).

These are WPT-relative test paths under testing/web-platform/tests. The exact existing tested fixture bodies are used, with no diagnostic native instrumentation, failure metadata, harness copies, tools, docs or benchmarks in this proposed production patch. A16/B16 remain in #163. This adds108 callbacks; the combined A16+B16+D64+C72+substitution20 roster is188. Callback counts are not defect counts. The proposal applies without fuzz to immutable #163 sources; it is a materialized review boundary, not adoption or a fresh runtime success claim.

The canvas2 fixture is useful additional direct-Block preservation coverage because stylist.rs changes that caller. It is not necessary to reproduce the core logical/physical defect and is not included in the strict five-file minimum. Before upstreaming it, remove its research-oriented window observation array/phase recording and diagnostic assertion description, then validate the cleaned body. Literal rejection and continued canvas usability alone do not prove the membership path ran. Prefer adding that small cleaned test if the final reviewer wants explicit coverage of the changed direct-block call site.

## What #163 supplies

C is integrated with #163's RevertState and longhand admission logic: cumulative origin/layer/important-inline exclusions survive Rule processing, and identity exclusions are added after the same cutoff guard. #163 also supplies the important-inline layer predicate needed by the mixed rollback D matrix and the D48 file that C extends. The exact C source patch refers to these bodies; source and test prerequisites are explicit, not optional tooling.

A pure source-owner/same-rule exclusion repair does not logically require every A/B behavior change. An alternative C-only implementation could be written against the old tuple cutoff representation, retaining its existing A/B bugs, and use a narrower test boundary. That would be a different implementation/intermediate state requiring separate native and browser validation, including preservation checks for mixed rollback behavior. Neither a clean textual apply nor the successful A+B+D-versus-C experiment would validate that alternative. Do not manufacture or describe it as already independently landable.

## Retained-base source checks

The immutable pre-project ancestor is `976279105b2e78b8666a959eb3f25c9176cefaf8` (2026-10-14), not the obsolete March origin/main merge base and not freshly fetched upstream.

* Exact C patch on #163: succeeds.
* Exact C patch on retained ancestor: fails5/11 cascade hunks.
* #163 on retained ancestor: succeeds; exact C after it fails3/11 cascade hunks.
* Those remaining failures are incidental import/insertion context: newer local PropertyIdRef/Namespace imports and the NonCustomPropertyReferences alias. No new C method requires those unrelated changes.
* `C-after-AB-retained-context.patch` resolves only those contexts, reusing the exact incremental helper bodies and C stylist change. It passes configured rustfmt parsing and byte-exact forward/reverse zero-fuzz application on copies of retained ancestor+#163. It does not add the unrelated imports, alias or branch repairs. Only import layout and helper/field insertion anchors differ.

Thus the concrete source-only alternative for an earlier branch is: apply #163 (its own two Rust files and three tests), then rebase the C production patch using the retained-context adaptation plus the C/substitution tests and D expansion. A single cumulative A+B+D+C patch could be materialized from that same chain, but would combine distinct defects and require a fresh coherent review/runtime boundary; it is unnecessary merely to satisfy the current branch's commit organization. Preserve the existing signed #163 history unless the user requests a rewrite.

No ArcSlice change is included or directly referenced by either source patch. This removes an apparent source-context dependency on unrelated local fixes; it does not prove an isolated build or all caller/lifetime behavior on the retained ancestor. Actual runtime validation so far uses the project branch with committed ArcSlice and other fixes. A current upstream rebase/compile/test remains separate, and C's incremental performance acceptance is still owned by the active experiment.

## Six occurrence tests

Keep the exact occurrence package in research for now. It is valuable coverage of repeated selector sources, cloned/cacheable sheets and implicit scopes, but the frozen JS emits CSS_OCCURRENCE_PHASE_V1 markers and includes support/cache resources designed for the sharing investigation. Computed-value success does not establish actual native pointer sharing, and the fixtures must not be described as six new bugs or a formal proof of rule-occurrence/allocation equivalence.

A cleaned, normative repeated-source WPT is a reasonable later production addition once expectations and the final runtime comparison are adjudicated. It should retain absolute expected results and independent-source controls, strip phase instrumentation and unnecessary research bookkeeping, and preserve only required support CSS/headers. It is not necessary for the minimal C defect regression commit above; adding it now would expand that production boundary with newly edited, unvalidated fixture bytes.

All findings are source/review scope. SOURCE-CHECKS, retained-context adaptation records and patch logs preserve the actual operations; temporary copies were removed. No new standalone bug or fixed-bug count is asserted.
