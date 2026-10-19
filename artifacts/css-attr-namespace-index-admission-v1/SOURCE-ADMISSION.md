# Source transition binding

Complete native candidate-v2 files are pinned in reload-probe-v1/source/. That probe subpackage remains frozen. Models below are manually source-matched fragments, not a verified Rust compiler translation.

| Native transition | Model | Boundary |
|---|---|---|
| OrderIndexMap var / attr namespace bucket / non_custom_index_map | IndexMaps and insert/lookup | Names and resolved namespaces represented by injective Nat tokens; external Hash/Eq and map semantics required |
| traverse occupied EntryRef return | enter occupied branch | Occurs only after map-value/dependency shortcut checks; finished-marker state is not consulted here |
| traverse vacant insertion; count++; var_info.push; stack.push | enter fresh branch | Atomic model covers completed allocation segment; no nested graph call occurs between those source operations |
| SCC pop and var_info.var.take | finishTop | Keeps the index map and vector position, sets node marker None, removes top stack entry; empty pop is totalized as no-op in the model and is not admitted as a native successful pop |
| Context::reset | reset/initial | Clears count, all index maps, vector and stack, while native substitution map persists; modeled slot reset keeps content and clears finished status |
| Attribute get_attr | getAttr | Flattens missing bucket/name and present None to None |
| get_attr().is_none() lazy load in visit_value_references | lazyOriginal | Provider result includes both DOM fetch and VariableValue parsing; failure makes no insertion, success writes raw value |
| Proposed raw entry-presence guard | lazyAbsentOnly | Separate proposal: absent only loads; present-invalid stays invalid. Native helper implementation is not part of this source snapshot |
| handle_loop/remove_attr; failed substitute_references_if_needed_and_apply | finish none | Completed invalidation writes a present None entry |
| successful attribute apply | finish (some value) | Source creates a new VariableValue from the substituted CSS; full guarantee that returned CSS is fully resolved remains an evaluator admission obligation |
| traverse map/universal/dependency checks | traversePrelude | Pending abstracts a value that reaches the occupied index branch; resolved/missing bypass index allocation. Other native shortcut effects and non-custom dependency flags are not represented |
| visit_link comparisons and active marker | visitLink | Direct branch order: larger index uses next lowlink regardless of marker; equal sets self_ref; smaller active uses index; smaller finished leaves state unchanged |

## Why absent and invalid must stay separate

- Fetch or initial parse failure never inserts an attribute value. Retrying that absent entry can be appropriate and is retained by the corrected model.
- Cycle invalidation and failed substitution deliberately insert None. Reloading such a slot discards a semantic invalidation decision.
- When a node has already completed, its numeric index remains in the map and VarInfo.var is None until Context reset. Replacing its tombstone with raw data does not allocate or resolve a fresh graph node: the occupied entry returns early.
- Checking namespace-bucket existence alone is insufficient. Presence must be checked for the specific local name inside that bucket, and present None must count as present.

## Strength and limits of the derived invariants

Allocator uniqueness, range and node ownership are derived from explicit initial state and modeled native state changes; they are not premise labels. The graph theorem in the previous package can use this result for map/index identity only after the relevant native control-flow projection is admitted. Arbitrary lowlinks and missing/reordered edges are not repaired by correct allocation.

The finished-value theorem is conditional on completed resolution operations storing terminal values. The old lazy-load transition independently refutes its preservation. The corrected guard restores preservation for that transition; it does not prove the entire native substitution implementation terminal. Native Vec/SmallVec limits, usize bounds and provider effects remain explicit external obligations.
