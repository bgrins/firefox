# Notification coverage for a state-preserving move

Seven Lean claims explain the observed source/destination asymmetry. They do not establish a new defect, C++ refinement or canonical coverage increment. Source inspection and browser observation preceded this model.

`refresh before after notify node` recomputes a marked node and otherwise retains its old cached value. `fresh_iff_covered` proves freshness on surviving nodes exactly when every survivor whose modeled value changes is notified. It is parametric in the value type: count, index, or their pair as the complete modeled context. An irrelevant context-field change need not force notification for a scalar that stays equal. `adding_notifications_preserves_freshness` proves set enlargement safe within this model.

Operational premises: cached values were initially fresh, notified nodes recompute from the post-operation context, and all relevant dependencies are represented. The theorem does not prove these premises, native dispatch, scheduling, floating-point evaluation, rule-cache behavior, or style sharing.

The concrete forest has four nodes. Initially parents contain [0,1] and [2,3]; node1 moves so they contain [0] and [2,3,1]. Node0 is the stationary old-parent element. Notifying only the destination updates nodes2,3,1 but leaves node0's cached count2 instead of fresh1. Every index still matches in this example because node0 remains first. Thus count failure can coexist with passing index controls. Moving the first child instead, from [1,0], makes node0's index change2→1 and exposes a second witness. Both-parent notification refreshes all modeled count/index values.

For same-parent reorder [0,1,2,3]→[1,2,3,0], the destination is also the source. Its notification covers every node, so count and index remain fresh. Passing this control cannot establish the old-parent path for distinct parents. The two false controls demand fresh values from destination-only notification in the cross-parent count and moving-first index witnesses; both are rejected.

Actual final replay `7ea7fc/0` checked seven declarations and rejected two controls using the pinned existing Lean toolchain in private scratch; scratch objects were removed. Initial `1f96fb/1` used unavailable `by_contra` and is retained as failed preparation. Final source has no sorry or native-decision axiom; Audit.log records actual axioms. No canonical coverage increment is claimed.

Preserving moved-root Servo data and its pending reframe is an independent native obligation. The model has no frames, animations, focus, iframe state, or restyle bits and cannot approve clearing or retaining them. The source proposal preserves that root while restoring existing old-container notifications; native build/browser validation remains separate. Selector invalidation generally and all DOM move algorithms are not proved.

Landing independence remains source-based: inherited font-weight count is computed even when reset structs are reused; width using sibling-index already excludes reset-cache insertion upstream. Those controls avoid the identified accepted146 reset-count dependency. Clean-upstream execution is not claimed. The selector family and existing WPT are prior art, not a new discovery from Lean.

All concrete forests explicitly contain each of four Fin4 nodes exactly once. The same-parent four-node example is an analogue of the browser reorder case, not an assertion that its topology is byte-identical. `index` uses List.idxOf+1 and is not a valid absent-node specification; absent nodes are outside these examples. Root bounded source review505496 found no blocker and confirmed that the generic theorem concerns changed values, not necessarily every context-field change.
