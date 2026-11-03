# Native/model correspondence boundary

Exact source excerpts and hashes are recorded in `SOURCE.json`; `REFERENCES.json` pins the existing audit, source snapshots, probe and prior publication model. This table maps names, not native correctness claims.

| Model | Exact e86 source | Established source observation | External obligation |
| --- | --- | --- | --- |
| Ordered `todo`, `convert`, receipt list | `values/computed/font.rs`, `FontSettings<T>::to_computed_value` | Original vector is mapped completely before dedup | Retained native cursor and ownership must preserve that order and call count |
| `lookupLast`, separate `effects` | `dedup_font_settings` | Stable sort followed by equal-tag swap/dedup retains last specified value | Sorted serialization and Rust vector mutation are not modeled; lookup semantics only |
| Total `Env.convert` | `values/specified/number.rs`, Number/Integer `ToComputedValue` | Returns plain value; calc resolution followed by normalization/clamping | Numeric arithmetic, f32 exceptional values and integer rounding are abstracted by Nat |
| `Expr.reads` | `CalcNumeric::resolve`, `Leaf::to_computed_value` | Selected calc leaves can read length metrics, tree counts and random context | Need actual selected-AST readset, not enum/tag-only classification |
| `scope`, `published_selected_scope` | `Context::resolve_tree_counting_result`, `query_sibling_count`, `query_sibling_index` | Current selected scope affects tree lookup; calls set flags and mark cache uncacheable | Actual scope installation/retirement across the retained property owner is unproved |
| Ordered effect events | `Context::query_font_metrics`, tree queries, `random_base_value` | Numeric conversion has context/cache effects in addition to result | Event-to-native-write mapping and lifetime/finality are not proved |
| Parent demand labels | Sealed numeric probe's `SPEC-TRACE.md` | Current Fonts/Values drafts choose parent metrics; e86 passes CurrentStyle | No native correction or blanket font-cycle policy follows from this model |

The full21 audit's source trace is extended, not replaced. Font-palette/emoji membership in a scanner does not make either a prerequisite for every metric. The probe distinguishes parser support and normative scope before reporting parent/child observations. No browser result is imported into this proof.
