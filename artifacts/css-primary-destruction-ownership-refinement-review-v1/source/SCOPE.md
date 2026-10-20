# Ownership refinement — scoped contract

Compilation began only after root released the timing hold. Existing source/proof/review capsules are unchanged. See REPORT.md for the checked component and replay gates.

## Intended invariant

The executor, heap cells and selected destructor plan remain exactly those of the prior proof. The refinement adds pre-state constraints, not a callback-preserves-postcondition axiom:

1. **Ordinary-array shape.** A decoded `none` buffer denotes the shared nonowned empty header, so its logical length is zero. A `some address` buffer has length no greater than its separately decoded capacity. This permits an allocated empty buffer. Apply this relation to the frame property table, shared line array and every line's item array.
2. **Local owner representation.** Every live modeled frame's table is shape-correct; its selected plan exists, has pairwise distinct owned addresses and names live allocation cells of the expected roles.
3. **Global owner separation.** For any two distinct live modeled frame identities, every owned address in one plan differs from every owned address in the other. Compare addresses regardless of roles: root/root, buffer/buffer and root/buffer aliases are excluded. Roles alone would not exclude two owners sharing the same role-correct root.

These constraints leave nonowning frame references unrestricted. Repeated, shared or dangling raw references do not become ownership claims. Capacity may limit the number of stored references, but not their identities or uniqueness.

## Derivation

Use the original stateful `removeAll`: clear the selected frame's table, then read and free each role-checked allocation. Derive:

* The selected plan is executable from the represented pre-state; native failure is not inferred from a model `none` result.
* An untouched frame retains its identical table and frame cell. Every allocation claimed by that table remains present with the same role, using pre-state cross-owner disjointness and the actual erased address list.
* No new frame cell is introduced. The selected owner becomes represented by an empty table; other represented owners retain their claims. Thus representation and separation hold globally after the selected phase.
* Primary coherence composes with the already proved cleanup result; it is distinct from allocation liveness.

This proves preservation from a substantive pre-state ownership invariant. It does **not** derive that invariant from native installation events. The new descriptor-access audit identified two fresh-new installers but also public typed setters, protected enumeration and generic cleanup, so privacy is not a substitute for event coverage.

## Source and projection limits

`FrameProperties::mProperties`, `SharedFlexData::mLines`, and `FlexLine::mItems` are the selected ordinary `nsTArray` storage sites. The retained array implementation states length ≤ capacity, uses a shared empty header and frees allocated storage in its destructor; empty logical arrays can retain allocated capacity. The precise actual header/buffer/capacity decoder remains external to this refinement. In particular, `Capacity : Address → Nat` is a mathematical input, **not a field read from the existing `Cell.allocation role`**, which has no payload or capacity.

The global invariant quantifies over all live frames **in the decoded selected-descriptor world**. The admitted destructor roster remains item cache, per-fragment data and shared flex data. It is not a theorem that all real frame properties belong to this roster. Foreign properties, ownership outside these decoded frame tables, specialized element traits, storage offsets, allocation bounds and real frame identities require a complete native projection before claiming global Gecko ownership. A hidden external owner would invalidate that projection, even if the modeled invariant holds.

`none` is a representation of no owned buffer, not a claim that native `mHdr` is null. AutoTArray/inline buffers are not silently identified with this ordinary-array relation. Address reuse and allocation generations remain open. The selected owner can survive coherently after its own captured cache is freed, so the stronger invariant still must not imply captured-pointer liveness through cleanup.

## Required distinguishing cases

* Reject each missing nonempty buffer: property table, line array, item array.
* Admit unallocated empty and allocated empty arrays; reject length exceeding supplied capacity.
* Reject distinct owners sharing a cache root or an item-array buffer. Include buffer/root cross-role aliasing and distinguish role rejection from address separation.
* Admit repeated raw frame references with adequate storage, including aliases across owners.
* Show untouched owner cleanup remains executable after deleting the first owner.
* Retain selected owner's freed-cache witness and address-reuse/generation limitation.

No native source changes, browser runs, Gecko builds or Git mutations are part of this component. The owned Lean replay checks the mathematical refinement. Full allocation F1–F16/F11/F12 and the synchronous callback/heap representation obligations remain open.
