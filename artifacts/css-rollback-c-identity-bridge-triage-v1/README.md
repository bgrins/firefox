# Cold C identity bridge: formal triage

Read-only review of `css-revert-rule-cold-membership-diagnostic-v1`, coordinated with `rollback_candidate_triage`. Its copied-source applicability check is separately recorded in `css-rollback-c-triage-current-v1`; this report does not repeat it or claim native execution. No new browser bug or demonstrated source-identity mismatch was found. The next useful proof is the native representation bridge below, not another proof of generic region deletion.

## A concrete invariant mismatch

The A+B+D bridge in `css-rollback-native-consumer-bridge-lean-v1` uses `fast == slot.isSome`. That invariant is **false for a reachable cold-C state**: the first admitted Rule sets the physical property's fast bit and appends `RuleExclusion`, while leaving its priority-cutoff map entry absent. This is a mismatch between proof domains, not a candidate bug.

For C the reachable-state invariant must instead be:

`fast(property) == (priorityMap.contains(property) || exclusions.any(e => e.property == property))`.

The candidate initializes all three empty. Every admitted rollback sets the bit; Rule appends an exclusion and other rollback kinds update the map. Guard-rejected declarations change neither. The per-property bridge must allow an empty priority state together with nonempty identity exclusions. The smallest discriminating state is: first Rule; then a normal alias in the same block; then a competing block. The first alias must be excluded even though no priority-map entry exists, while the competing block remains eligible. Existing C72 cases already supply browser evidence for this behavior; this is not a request for duplicate WPTs.

## Mapping the actual exclusion relation

For a fixed cascade instance and physical property, instantiate `RepresentedControl` with identity `(full normalized CascadePriority, declaration-block allocation class)`. In a multi-property presentation also include the physical property. The priority identity must retain origin, context/order, layer **and flags**. Native `CascadePriority::cmp` ignores flags, but derived `PartialEq` used by `RuleExclusion` does not. Scalar cutoff keys cannot replace this identity.

`block_contains` compares addresses of **original** entries of `PropertyDeclarationBlock::declarations()`. `apply_one_longhand` saves the original declaration before substitution; exclusions are tested before substitution. This correctly avoids identifying declarations by equal CSS values or owned substitution results. The cold search returns a block, not a rule-node priority: when several nodes reference the same block, finding an earlier node with a different priority does not overwrite the triggering event's priority. That suspected mismatch is therefore absent from the inspected code.

The missing membership bridge has these concrete premises:

* Every original declaration reaching a longhand Rule comes from the current source view: the same rule-tree ancestor walk used by `DeclarationIterator`, or the actual direct block passed by `Stylist::compute_for_declarations`.
* Original declaration entries remain live, unmoved and immutable for the cascade/exclusion lifetime. Stored exclusions borrow blocks; the rule-tree sources and origin-specific read guards remain borrowed. Direct-block compute retains its own guarded source. No cross-cascade address reuse is relevant because exclusions start empty in each `Cascade`.
* For nonempty declaration slices, pointer membership identifies the intended block allocation class. Distinct simultaneously live owning slices cannot share an entry address; aliases of the same block can. `PropertyDeclarationBlock` stores a `ThinVec<PropertyDeclaration>` and clones that container. This source review has **not** formally verified allocator, shared-memory serialization or container aliasing semantics. If distinct block objects could share a nonempty entry slice, cold membership could merge them where the historical block-pointer key would not; no such construction was found or asserted reachable.

Under those premises, first-match search is total for producer declarations, and the membership scan equals identity equality. Duplicate rule-tree nodes are harmless to lookup correctness. Establishing semantic equivalence between shared allocation classes and distinct CSS rule occurrences remains the separate quotient obligation; membership correctness alone cannot discharge it.

## Logical mapping, phases and visited styles

| Path | Inspected behavior and proof obligation |
| --- | --- |
| Ordinary logical declarations | `apply_non_prioritary_properties` records the writing-mode dependency and maps to a physical ID before `apply_one_longhand` checks exclusions. Use that resolved mapping in the identity; preserve the observation before exclusion. Other physical properties in the same source block must remain eligible. |
| Prioritary declarations | `apply_one_prioritary_property` asserts nonlogical ID, follows the declaration chain, and runs postprocessing only after the property becomes seen. The same exclusion consumer receives its original stored declaration reference. No logical alias mapping is required on this path. |
| Important/normal | `DeclarationIterator::next` reverses the block iterator and selects its matching importance. Exclusion keys call `unimportant()` but retain the original block, layer, context and flags. `RepresentedControl` can model this exact allocation key; it does not prove that both native importance visits cover the same semantic occurrence roster. `constructed_stream_quotient` proves the reduced quotient only for its explicitly paired rosters and fixed actions. Native empty partitions/restrictions must be accounted for, not treated as evidence that every node literally occurs twice. |
| Visited | `compute_visited_style_if_needed` recursively calls `cascade_rules` with `visited_rules`; that call creates a fresh `Cascade` and source view from that same root. It copies substitution functions/writing mode from the unvisited context, not its exclusion vector. The visited declaration filter may leave an empty stream. No unvisited-root provenance leak was found. |
| Direct block | `compute_for_declarations` supplies `Some(block)` while using an otherwise empty rule root. This fixes the source-view distinction; the existing direct-coverage proposal is the appropriate positive substituted-Rule witness. |
| Custom-only | The constructor stores no sources and its builder does not populate the longhand buffer. Custom Rule does not use `RuleExclusion`. Extending the longhand identity theorem to custom properties would overstate this patch. |

Both the repeated-block model and the observation audit remain necessary. Equal normalized priority makes the A+B+D eligibility predicates importance-insensitive, but the complete native evaluator has observations, substitution context and deferred color actions not represented by a pure fixed action stream. This report does not upgrade those conditional results to universal native correctness.

## Smallest next proof and test

Add one isolated representation proof with three results:

1. Derive the union fast-bit invariant from empty initialization and guarded Rule/non-Rule updates.
2. Define finite source blocks with original entry identities and a covering source roster; derive first-match lookup correctness from disjoint ownership, without requiring unique rule-tree nodes. Derive cold membership exclusion equality with the full property/normalized-priority/block key.
3. Use those results to show the actual conjunctive cutoff-plus-cold-exclusion gate matches `storedAllowed`, and the two update arms match `storedAdd`. Then reuse `stored_control_deletion`. Do not present the separate CSS occurrence-to-allocation quotient as proved by this representation theorem.

Keep the direct canvas substituted-Rule regression proposed in `css-revert-rule-cold-membership-direct-coverage-v1` as the smallest new runtime coverage. Beyond that, a visited logical/physical **border-color** same-block versus separate-block test would cover a presently unobserved provider: important Rule followed by the normal physical alias, plus an unrelated physical side control. It needs an existing privileged visited-history/visual test harness; ordinary `getComputedStyle` intentionally hides visited colors and is not a valid oracle. This report creates no test and supplies no new normative numeric oracle.

No native, browser, build, Git, canonical Lean or old artifact changes were made. `INPUTS.json` pins the exact reviewed snapshots and `SOURCE-EXCERPTS.json` retains the additional immutable declaration-container evidence. No new Lean theorem was asserted or compiled for this triage-only task.
