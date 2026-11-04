# Cold C benchmark path and scan cost

Read-only audit of `css-revert-rule-cold-cost-benchmark-v1/benchmark.html`, coordinated with the wrapper agent. The workload has a credible source argument for exercising cold C on every completed Rule-mode update; changing computed values alone do not prove entry counts. No benchmark, browser, build or native instrumentation was run here. `SOURCES.json` pins the actual page, copied C candidate and immutable a6 source used for these conclusions.

## Why the custom-property toggle should reach opacity again

Every sample installs a fresh stylesheet and flushes once, then performs four warmups and the timed updates. Every update alternates inline `--floor` between 0.25 and 0.75 and reads opacity. Each matched block has one opacity declaration and a distinct `--block` value. Literal mode uses `opacity:var(--floor)` in the winning top block; Rule and Layer modes reach the lower named layer's `opacity:var(--floor)`. Count zero reaches that lower declaration directly. Those are reset, non-inherited longhands.

`Cascade::substitute_variables_if_needed` calls `set_uncacheable` whenever it processes a non-inherited `WithVariables` declaration, before substitution. The winning opacity declaration supplies that condition in every successful mode. `RuleCache::insert_if_possible` refuses those styles. A fresh sample's new rule chain and successful initial flush therefore should not populate a reset-style entry that can bypass later opacity cascades.

The qualification matters: `RuleCache::get_rule_node_for_cache` **can skip a custom-only inline block**. Toggling `--floor` alone is not proof against cache reuse. The reached reset-variable declaration and cache-insertion refusal provide the source argument. A real reset-cache hit would select only late inherited properties in `apply_declarations`, skipping opacity; instrumentation should count that branch if results are ambiguous.

`CascadeOnly` also does not mean custom-properties-only evaluation. The traversal calls `StyleResolverForElement::cascade_styles_with_default_parents`, which ultimately runs the ordinary cascade when it cannot reuse a shared primary style. The rule-identity sharing fast path requires another candidate with the same complete rule chain and inherited style. This page has one uniquely ID-matched probe and no matching sibling donor; the sharing cache is not a history of the probe's two previous opacity values. Its inspected lookup explicitly expects candidate and target to differ. These source facts support the workload, but are not a logged observation of the chosen path on any particular update.

The Rule workload is deliberately semantically benign: one opacity declaration per distinct block, no logical aliases. A+B+D and C should both return the changing lower value. It measures the cost of C's newly added lookups/exclusion checks; it does not reproduce C's original wrong-value bug. The four warmups exercise the same work before timing. Setup stylesheet parsing is separately timed and excluded from measured update timing.

## Exact operation model

For an arbitrary fresh cascade, let `R` be the number of admitted Rule triggers. Each trigger scans source nodes from the source view's beginning until the original declaration's owner is found. Its pointer-comparison count is the sum of all earlier source-block lengths plus the matching entry's one-based position. Repeated appearances of the same block are charged again by this implementation.

For every cutoff-admitted longhand reaching the C guard, count exclusion records up to the first matching record, or all records if none matches. Only records with the same physical property and **full normalized priority** call `block_contains`. Each such call scans its block until the exact entry is found, or scans its entire length on a miss. Priority-cutoff-rejected declarations never reach that scan. These two sums specify the operation model without asserting that all source blocks have equal size.

For this page's simple Rule chain, assume one one-entry inline `--floor` block precedes `N` distinct two-entry blocks, each storing opacity first and `--block` second. Number Rule triggers from strongest to weakest, `j=1..N`:

| Operation | Per trigger / cascade prediction |
| --- | --- |
| Source blocks visited for trigger j | j + 1 |
| Source pointer comparisons for trigger j | 1 + 2(j−1) + 1 = 2j |
| Prior exclusion records checked for trigger j | j−1 |
| Exclusion pointer comparisons for trigger j | 2(j−1), all misses |
| Lower-layer winning declaration | N exclusion-record checks, but zero membership scans because its normalized layer differs |
| Total source pointer comparisons | N(N+1) |
| Total exclusion pointer comparisons | N(N−1) |
| Total membership pointer comparisons | 2N² |

`MODEL.json` evaluates those formulas at the requested counts. Extra source nodes or different stored declaration order change the exact coefficients; the general sums above remain the definition. Literal mode has no Rule trigger. Layer mode updates priority cutoffs and rejects the remaining unlayered chain before identity checks; its exclusion vector remains empty. Their baseline cascade/collection work is still nonzero and grows with rule count.

The measured duration also includes JS calls, inline mutation/invalidation, rule updates, custom-property and declaration processing, style adjustment, serialization and timer overhead. The operation model is not a timing estimate, a measured count, or a proof that all observed growth comes from these scans.

## If timing attribution is ambiguous

Use a separate diagnostic run with aggregate counters for the retained probe/flush: fresh cascade calls, primary-style reuse, reset-cache hits, opacity consumer visits, admitted Rule triggers, source lookup calls, source nodes visited, source pointer comparisons, exclusion records tested, and exclusion pointer comparisons. Distinguish the two `block_contains` callers. Join each aggregate with mode/count and the checked output, and keep setup/warmup/timed-update phases separate. Expected Rule trigger count is N per fresh cascade; expected source lookup count is the same. A flat timing with those counters present is different from a flat timing with the path bypassed.

Do not emit a log per pointer comparison or use an instrumented elapsed time as the acceptance measurement. The wrapper's report/completion checks authenticate workload completion, not native path entry. Run timing comparisons separately without the diagnostic counters/logging once coverage is established.

## Plausible lazy-index improvement

On the first admitted Rule, lazily build an original-entry-address → borrowed block-identity map from the current Rules/Block source view, enumerating duplicate block allocations once. Maintain an exclusion hash set keyed by `(physical property, full normalized priority, block identity)`. Resolve a later original declaration through the owner map, then perform one exclusion-key lookup. Preserve the existing fast bit and cutoff guard; a cascade with no Rule still needs no index allocation.

With S source nodes, D entries across distinct blocks, E eligible C checks and R Rule insertions, this changes expected lookup work to O(S+D+E+R), with O(D+R) auxiliary storage plus block-deduplication state. This is expected hash-table complexity, not a worst-case proof or a measured improvement. Indexing only owner recovery leaves the linear exclusion vector's quadratic work intact. The improvement must retain original-reference lifetimes, full flag-sensitive priority equality, logical mapping/observation order, visited/direct source views, and per-cascade ownership. It could cost more for small cascades, so it is a proposal, not an accepted patch.
