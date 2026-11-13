# Clause and proof mapping

| Input / clause | Executable | Independent relation / checked law |
|---|---|---|
| Already ordered full item list | Generic α and size:α→Rat | collect_flatten preserves exact values/order/repetitions |
| Fixed main-axis gutter between consecutive items | span/takeMore | span_sum_count, span_snoc; no gap at either edge |
| First item exceeds inner threshold | collect oversized branch | next_oversized; oversized_singleton |
| Stop on first failing next item | takeMore | PrefixesFit + next-extension failure in NextLine; firstLine_complete |
| Negative prefixes permitted | No zero-floor or individual-item guard in takeMore | negative_prefix; no_prefix_floor |
| Repeat collection on remaining input | collect, decreasing remaining length | Collected; collect_iff; next_rest_shorter |
| Nonempty emitted lines | Both branches cons first item | collect_nonempty; collect_count |
| nowrap | nowrap | nowrap_flatten; occupied-line empty convention explicit |

The primary snapshots and source spans are retained by the frozen design capsule. ORIGINS.json authenticates its manifest and all members plus its immediate primary-source/tool origins. The copied DESIGN documents are unchanged. TARGET-INPUTS.json freezes Model.lean and Target.lean before substantive proof implementation; both still match. Model contains only one private length lemma needed to justify termination. All semantic proofs are separate modules.

The independent specification is not a second parser or arithmetic implementation: it uses the same exact span function but characterizes all nonempty prefixes and the stopping condition rather than referring to takeMore/collect output. The fold-to-sum theorem makes the gap arithmetic reviewable. Lean does not prove the English-to-relation interpretation or the interpretation of actual acquired native sizes.

Specification scope: frozen Flexbox1 collection snapshot dated8May2026; current Alignment3 snapshot dated21October2026 points its gaps section to CSS Gaps1. The separately retained Gaps1 primary excerpt supplies fixed-gap semantics. It links Flexbox2 terminology; this research does not silently replace the original Flexbox1 algorithm. webspec-index readonly-cache refusal is preserved in the design capsule. Native root reproduction/fix work is independent and no native acceptance is asserted here.
