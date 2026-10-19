# Name-only cache port: source correspondence

## Exact delta

The original ComputedSubstitutionFunctions.attributes is OwnMap keyed solely by Name. remove_attr(name) inserts None; get_attr(name) flattens absent and present None to the same returned None. The port adds contains_attr(name), implemented as `self.attributes.contains_key(name)`, and changes only the lazy-load guard in visit_value_references to `!context.map().contains_attr(&next.name)`.

The candidate source is reconstructed by exactly those two substitutions. All other original bytes are required to match. There is no namespace bucket, namespace parameter, new public API, graph/index change, fallback traversal change, or evaluator change in this patch. The helper is crate-local and has one caller. It does not change the layout of ComputedSubstitutionFunctions.

## Preserved behavior

| Original name-only entry | New lazy-load behavior |
| --- | --- |
| Missing | Attempt provider/read/parse; insert only on success |
| Present None | Preserve explicit invalidation; do not reload raw tokens |
| Present Some(value) | Preserve value, as before |

Initial parse failures and missing provider values still create no entry, so they remain retryable. A different name's entry does not suppress a load. Unknown namespace/provider handling is not changed or reimplemented; it still uses the original get_attr_value_for_cycle_resolution path whenever the entry is absent. No new negative caching is introduced.

All original value readers remain get_attr: resolved-primary classification in visit_value_references, attribute shortcut in traverse, and typed substitution lookup in custom_properties.rs. They continue treating explicit None as invalid. The two invalidating writers (cycle handling and failed substitution) still insert None. Successful apply and eager preload still write through insert_attr. The port changes neither those writers nor preloading/deduplication. The original Gecko glue direct-map interface is unaffected.

This is the same absent-versus-invalid transition as the namespace-aware proposal, applied to one map instead of a namespace bucket's inner map. The existing ReloadState theorem about preserving any present entry and retrying absence applies to this local abstract transition. It does not make the name-only key space injective across namespaces: the independent namespace collision defect remains. Consequently no statement about correct qualified-name identity or arbitrary cross-namespace histories follows from this port.

Preserving a tombstone makes traverse return at the value lookup before using a retained graph index. The finished-node/value argument retains the prior qualification: completion must store terminal values and invariants are asserted at completed-visit checkpoints. The port does not prove full Tarjan/substitution/provider/observer correctness or container-query chained attribute behavior.

## Landing and tests

The ten-test final WPT is byte-identical to the namespace-aware package's version. All its attributes are in the null namespace, so it tests repeated invalidation independently of namespace collisions. No baseline or candidate browser result is asserted for this source variant; the known frozen diagnostic baseline was executed against the later namespace-aware source. Root should baseline this final WPT and validate the port on its selected source build.

This is a ready textual port for landing the tombstone cause before the namespace cause. If that order is chosen, the namespace patch will need the corresponding mechanical update of contains_attr and its caller to the qualified API. The two patch variants are alternatives, not patches to apply sequentially. The namespace-aware sealed candidate remains the expected final combined representation.
