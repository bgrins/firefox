# Independent transient recascade source review

No blocking source issue found for the proposed bounded experiment. This is review of an internal maps-in/style-out prerequisite, not acceptance of bug 1615083 or public CSSOM behavior. No native compilation, browser execution or live source/index/app mutation was performed by this review.

The reviewed source manifest is `6aeedef5df63410009fd1e65f15aa2fd263a951b90f21fb9e15e90de86b744e3`, with native patch `ad5e8990539093a7dbf9b929ca934a0b84f133b6b36921b542c8a179ea42fa54` and combined extension `268ac950769d45202d6adfb17b5b0b3269f2ab9fd0eaed624806115d5a24a2f5`. `audit.py` authenticated all 66 inputs and 12 pinned Git objects, replayed the author's source checker in owned scratch, and independently compared full file inventories through forward and reverse patch application. The copied checker differs only in its repository-root locator. Scratch was removed, and frozen inputs were rechecked afterward.

## Native data flow

`ServoStyleSet::RecascadeStyleForMissingPseudo` checks document connection, dynamic context, traversal/stylist state, pseudo kind/identifier, missing generated element and style pseudo tags. Rust additionally requires that the supplied primary pointer equals the element's stored primary style. This establishes correspondence with the stored allocation, not freshness of all ancestors or unique element provenance: style allocations may be shared. The caller must still supply the same-target, same-epoch pseudo base and coherent current ancestry.

`CascadeInputs::new_from_style` clones the normal and existing visited rule paths, retains only `flags.for_cascade_inputs()`, and resets `included_cascade_flags` to empty. The prototype does not copy every computed flag or promise arbitrary special-filter/starting-style contexts. That matches its ordinary lazy-style input convention.

Each supplied map becomes a fresh normal-importance declaration block. `update_rule_at_level` replaces/removes the single rule at exactly the animation or transition origin and reconstructs the higher-priority path. Its existing single-rule-at-priority premise applies to these origins. Important and other origin/layer rules remain intact. Empty maps remove the corresponding rule; they are not treated as a reason to reuse the old origin value. Both present paths are updated, while a nonexistent visited path remains nonexistent.

The final cascade uses `cascade_style_and_visited_for_pseudo_with_default_parents`, not the ordinary-element resolver. Inheritance comes from the explicit originating primary style. The existing helper chooses the real layout parent when that primary style is display:contents. This preserves pseudo adjustment rather than passing pseudo rules through an ordinary element cascade.

Fresh declaration blocks are retained through owned rule nodes. The primary `ArcBorrow::from_ref(...).clone_arc()` relies on the existing Gecko/Servo computed-style Arc allocation convention; the temporary driver holds the corresponding `RefPtr`. The snapshots pointer is checked nonnull and used synchronously under the document/style-set lifetime. No raw pointer is stored by the new API. Maps must contain valid matching property/value pairs, as produced by the driver or existing composition machinery. These are native ownership/precondition arguments, not a proof against arbitrary invalid FFI inputs or reentrant retargeting.

No new call publishes a computed style to ElementData or runs selector matching, effect sampling or endpoint conversion. The local context/cache is temporary. Nevertheless, rule-tree allocation and the traversal guard's existing deferred tasks remain observable implementation activity; “request-local output” must not be described as global purity or a universal no-callback guarantee. The source report preserves this distinction.

## Test reachability and oracle scope

The final AST inventory contains 100 unique assertions in six tasks. Six explicit setup observations precede relevant results, including generated-pseudo existence before its rejection. Four repeated admission/preservation observations cover each successful result. The empty-map flag performs a second recascade on the first returned rule path, so it exercises actual removal of populated origins. Disjoint and overlapping maps have separate observations.

The donor styles supply already-computed values directly. The tests check origin priority, inheritance, authored relative-value and custom-property substitution, RTL mapping, layout-parent adjustment, pseudo identity, rejection and limited non-publication observations. They do not establish sampled-effect-to-recascade integration. The accompanying unchanged 208-query assertions and 130-record WPT vector are separate preservation gates, not a proof that all those seams compose correctly.

The origin-order oracle follows [CSS Cascade 5 cascade sorting](https://drafts.csswg.org/css-cascade-5/#cascade-sort): transitions outrank important author rules, which outrank animations, which outrank normal author rules. [CSS Pseudo 4 tree-abiding inheritance](https://drafts.csswg.org/css-pseudo-4/#treelike) supports originating-element inheritance. [CSS Display 3 display:contents](https://drafts.csswg.org/css-display-3/#valdef-display-contents) distinguishes unchanged inheritance from box-tree substitution. The absent-pseudo display result remains an internal resolver-consistency check; it is not promoted to a universal public resolved-style rule for a nonexistent box.

The current fixtures contain no visited-link oracle. Updating the existing visited path retains the established cascade machinery, but public CSSOM privacy/sanitization is not validated. Origin-pointer and selected public-value observations are useful checks, not exhaustive non-publication proofs.

## Remaining gates

Proceed with genuine installed lint, generated bindings/native compilation, exact 100-assertion/6-task completion, unchanged 208-query assertions and exact 130-record WPT preservation, with full restoration. Every setup, task completion, harness status, unexpected error/crash and missing/duplicate callback must remain independently checked. A baseline executable without the new diagnostic interface is not a valid baseline for the 100 direct assertions.

Provider coherence for endpoint conversion, combined effect sampling/recascade timing, cache/generation invalidation, general pseudo admission, visited exposure and the historical debug transform/change-hint regression gate remain open. This review does not authorize widening a final missing-pseudo fix claim or counting another fixed bug.
