# Independent public-storage checkpoint review

## Recommendation

Accept this checkpoint's limited universal model claims. No substantive proof/model mismatch found. It is not a completed native operation-sequence or CSSOM proof. The reviewed source checkpoint is copied under checkpoint/ so later work in the producer's active directory cannot silently change this review.

Root supplied CHECKPOINT SHA 980f02f654d2dcb9936dbf1009f38317adf46972e9a4cb7c1f15de8cd68774e1 and replay.py SHA 5e0662187e3efcac16483b4c1730833bfb678e5157221ea2f06d34c76807e9e6. Both matched before execution; all three Lean source pins authenticated. Fresh external relocation compiled AllOrder, PublicStorage, PublicRemoval and the exact audit inventory: 26 plus nine results, all within the standard allowed axioms. Raw commands and audits are retained. No native or browser build/run occurred.

## Complete new model reading

Read both new modules in full and the inherited Entry/Plan/Storage/Represents/execute/rawStep/decode and refinement helpers used by them. The inherited AllOrder module is copied unchanged at its accepted source hash. No unrestricted native payload-equality admission is imported: new definitions require decidable identity equality only; classical equality introduced in proofs supplies inherited helper parameters without requiring a runtime payload comparator.

PublicStorage's parseSet is a direct forward priority-aware setter. pushScan selects no-op only for important-to-normal rejection and otherwise an append or indexed move. rawPush explicitly performs membership insertion before the scan, and the proof derives the inserted map is unchanged on the existing-ID branch. Distinct declaration/importance lists and exact ID membership are maintained by Represents. Push refinement and uniqueness are lifted over arbitrary finite source streams, including duplicate input identities. parse_other_values preserves a supplied projection excluding the overwritten ID.

rawDelete removes aligned list positions and clears the specified ID. Its refinement requires the exact split and initial uniqueness, establishing that no other remaining entry needs that membership bit. deletion_target derives bounds and both payload/importance reads. removeLoop threads the retained prefix and remaining source suffix; its cursor is prefix length, unchanged on removal and advanced on retention. Refinement proves stable filtering, and SafeRemoval proves bounds/target association at every modeled iteration. Earliest-removal refinement uses the explicit no-match prefix premise. clear establishes empty three-field representation.

The history theorem is an induction over exactly parse/remove/clear constructors and proves every prefix through take. It does not quantify over CSSOM batch update, a separate cached-index callback action, animation-map construction, flags, or returned change booleans. PLAN states this accurately.

PublicRemoval's firstIndex independently scans selected identities. The certificate proves earliest matching decomposition; the converse proves query agreement. The query/removal theorem derives valid indexed removal from that certificate. callback_stable_removal transports the query across unchanged ordered IDs, while allowing values/importance to differ provided after-storage represents a unique valid list. This is sufficient for structural removal safety but not proof that a CSSOM callback may arbitrarily change other declarations. The concrete stale_index_witness only establishes the index changes after an earlier entry disappears; it does not execute a native crash.

## Source correspondence and precise open joins

Compared against the frozen public-operation source audit. Priority handling, membership insertion, replacement append order, aligned removal, unchanged-index deletion scan and clear agree with the inspected code at the selected abstraction.

The remaining joins are material and appropriately not claimed complete:

1. Native first_declaration_to_remove has a membership early-return for nonshorthands; firstIndex is a pure forward query. Exact membership plus unique storage must connect those paths.
2. Native longhand/custom removal returns immediately after the first deletion. Model removeAt processes the suffix for every selected predicate. The native equivalence requires a singleton-identity target and uniqueness to prove no suffix match; shorthand predicates use the actual generated membership relation.
3. The modeled remove loop consumes a ghost source suffix with cursor prefix.length. Native while iteration reads the changing vector and len. SafeRemoval supplies the core invariant, but actual usize arithmetic, container indexing and loop translation remain pending.
4. The history's remove operation is full filtering via rawRemove. PublicRemoval proves optimized queried/cached variants separately; their composition into callback-aware native histories is still open.
5. Target-roster callback stability is assumed, not derived from FFI type or all native observer implementations. The script-blocked inline callback evidence is a separate source argument.
6. Explicitly excluded: native changed-return bits, immutable flag, allocation/failure/heap/compiler semantics, parser value validity, animation-map key/uncompute coherence, and ordinary CSSOM update composition.

No source weakening or new bug acceptance follows. The next useful work is the above source-query and singleton-target transfer, then a single joined legal-operation history that carries a fresh removal certificate across admitted callbacks.

## Replay/checker assessment

replay.py pins source and Lean binary before compiling, uses a fresh output and explicit cwd/LEAN_PATH, checks exact theorem names and permits only standard axioms. CHECKPOINT is a versioned active checkpoint rather than a closed final manifest; this independent capsule seals the reviewed inputs and receipts. No semantic mutant or native differential claim is made. Existing kernel witness and full proof reading suffice for this bounded review; no optional broad test matrix was added.
