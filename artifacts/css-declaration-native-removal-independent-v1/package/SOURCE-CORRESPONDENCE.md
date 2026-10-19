# Native source correspondence

Ten complete source definitions are retained in SOURCE-BINDINGS.json, with their original source slices and SHA-256 hashes. Complete declaration_block.rs and properties/mod.rs snapshots come from the authenticated earlier public-operation audit. These are manual control/data correspondence bindings, not a verified Rust translation. No native compilation is claimed here.

| Native operation | Model | Admission |
| --- | --- | --- |
| first_declaration_to_remove membership early-out for non-shorthand | NativeRemovalAPI.query single branch | exact represented membership, fixed property identity |
| declaration iterator position using is_or_is_longhand_of | seek on current raw declaration payloads; seek_projection | iterator observes the same ordered vector, identity extraction |
| remove_property cached first index and debug assertions | queried connection / firstIndex certificate | actual callback preserves ordered IDs and storage validity; assertions alone do not prove this |
| first unconditional remove_declaration_at | rawDelete before property-kind split | index certificate and concrete deletion method semantics |
| non-shorthand immediate return | NativeRemovalAPI.remove single branch | unique destination IDs, singleton property selection |
| shorthand i = first_declaration; len = self.len() | loop called with actual deleted-vector length | representable native length/index |
| while i < len | well-founded loop guard | native usize comparison agrees with Nat |
| current self.declarations[i] read | raw.declarations[i]? | Safe proves Some under admitted representation; model fault represents invalid native-read admission, not native recovery |
| nonmatching entry i += 1; continue | keep_transition | i+1 <= len derives no overflow when len fits usize |
| matching entry remove_declaration_at(i); len -= 1 | delete_transition; same recursive index | len positive derives non-underflow; concrete normal deletion semantics |
| remove_declaration_at removes membership, bit, declaration | rawDelete transforms each separately | single atomic model step only under normal-return container and no-observer/interleaving admission |

PropertyDeclarationId::is_or_is_longhand_of and is_longhand_of are retained alongside LonghandId's delegates and PropertyId::as_shorthand. For an actual shorthand the query's membership test delegates to the same is_longhand_of used by the loop, and custom IDs are false. For a longhand/custom property the query is singleton identity matching and the caller returns after its first removal. The model permits any fixed shorthand membership function. It does not establish metadata generation, name equality, concrete enum layouts, or future preference changes during the call.

The native loop mutates a local len independently from the current vector. The model retains that distinct local variable and an explicit absent-read outcome. Its well-founded measure is len-index; no suffix is passed to executable loop. The proof uses pre/rest only as an invariant relating the direct execution to the previous accepted reference. Safe is an inductively finite sequence of actual modeled current-vector states and carries separate declaration/importance read bounds and length equations at each state.

Native mutation correspondence: adding i += 1 after the deletion skips a shifted adjacent target; omitting len -= 1 eventually attempts a read beyond the shortened vector. The kernel witnesses use those altered transitions, not a modified expected output. The omitted-length example is intentionally fuel-bounded because a malformed native loop has no justified original len-index termination argument. It reaches a real absent current-vector read before exhausting its supplied fuel. A separate compiled Lean source mutation advances index in the original loop; the exact original refinement proof fails semantically, and the successful counterexample establishes why.
