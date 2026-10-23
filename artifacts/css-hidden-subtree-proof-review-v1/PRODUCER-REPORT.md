# Hidden flex child-subtree model

**Scoped result established; full native lifecycle and geometry correctness remain open.** This artifact models the actual candidate's `MarkPrincipalChildrenDirty()` at the hidden `ReflowChildren` return. It does not combine it with the earlier miss-only direct dirty mark and does not turn the passing browser matrix into proof.

## General results

The successor has **36 new Lean kernel results**, plus **30 byte-identical imported results** from the earlier direct-item model. The new results distinguish `NS_FRAME_IS_DIRTY` from `NS_FRAME_HAS_DIRTY_CHILDREN` throughout.

- A principal root becomes query-eligible unconditionally in the tree projection. Its own table-column-group tag does not suppress the initial root call.
- Previously eligible paths remain eligible. Setting only HAS_DIRTY_CHILDREN does not cause the helper's dirty-root shortcut.
- A descendant along a path with no initially dirty or table-column-group barrier becomes eligible.
- `root_coverage_exact` characterizes **every direct dirty bit** after marking using the initial barrier subtrees. A pruned dirty subtree must already have every descendant bit; a pruned table subtree can likewise retain clean frames. This is not an inferred global native invariant.
- `producer_marks_every_bit` proves that the nonpruning `FrameNeedsReflow(IS_DIRTY)` descendant walk establishes every bit, even through already-dirty and table nodes. It therefore establishes the helper's sufficient barrier condition.
- Conditional selected-query recovery composes with the earlier Hidden model and returns the arbitrary layout provider's actual result. It requires the same frame/bit projection, hidden ancestor, actual forced traversal and successful provider completion; no desired-size equality is assumed.

The every-bit predicate is deliberately stronger than query eligibility. A clean node with HAS_DIRTY_CHILDREN is eligible even if `allDirty` is false. Neither the exact-bit theorem nor the barrier condition is claimed to be a necessary condition for every geometry query to force layout.

Countermodels preserve: an already-dirty principal root with a clean leaf; a dirty interior root; a table-column-group barrier; an external out-of-flow target; a missing hidden ancestor; and other continuation/list roots that are not visited. They identify boundaries, not independently demonstrated native bugs.

## Source and native calibration

The source candidate is authenticated from `css-hidden-geometry-skipped-layout-review-v1`, FILES `69eb758a60657dace7e5f59f2c701c96d7ae586532fff8c5f8bcb058d8ea0daf`. `PATCH-BINDING.json` confirms exactly one statement differs between its complete original and candidate files. These are retained local source roles, not an assertion of isolated browser execution or upstream patch independence.

The native frame and PresShell snapshots are copied from the earlier authenticated proof inputs. Both marking helper bodies match the retained indexed source byte for byte. Complete indexed sources and query outputs are retained separately as discovery evidence; no current live instrumented source is substituted.

There are **15 source bindings**: eleven complete methods/functions, the exact producer root statement, its exact descendant-walk branch, and the original/candidate initial caller guards. Eight complete methods compile in the facade; seven execute. The hidden in-flow-parent predicate is retained but not invoked. The three large caller/producer bodies are bound in full but only the explicitly identified branches execute. This distinction matters: whole-body hashes do not prove whole-body behavior.

Each canonical and manifest-only relocated replay compares **6,144 Lean rows at O0 and O2** against extracted C++, with UBSan enabled: **12,288 matching rows per replay**. The matrix independently varies hidden state, six descendant direct dirty bits plus the container bit, two HAS_DIRTY_CHILDREN bits, table placement and whether the nonpruning producer ran first. Each row observes nine graph nodes' direct dirty bit, eligibility and scheduled forcing, plus the container's direct bit.

The graph includes principal siblings, a second child list below a principal root, a placeholder role whose external target is not a child-list edge, the container's other list, and another continuation role. These are explicit graph/provider roles; they are not a proof of every real frame-construction path. No geometry API is invoked in this executable. Document flushing is a no-op, so the source calibration proves no actual CSS layout result.

Seven semantic mutations compile and execute at both optimization levels and are detected: omit the candidate mark; set only principal root bits; prune HAS_DIRTY_CHILDREN; walk only principal lists; ignore table barriers; ignore dirty barriers; and force clean queries. Four false theorem claims are rejected specifically as false by Lean. Fifteen integrity controls reject the intended gates, including resealed role substitution, a modified imported model, a resealed extra cache, nonregular FIFO input, proof escape and output overlap.

## Actual dirty-state producer assessment

`PresShell::FrameNeedsReflow` first checks initialization and destruction state and asserts a valid non-reflowing caller. The modeled producer is its IS_DIRTY/IntrinsicDirty::None branch **after those entry gates**. It sets the root bit and then walks all actual child lists without pruning already-dirty roots. Ancestor scheduling and reflow-root handling are outside the model. This is a theorem about that executed state transition, not an unconditional API postcondition when the method returns early.

`RestyleManager::StyleChangeReflow` sends its IS_DIRTY path through FrameNeedsReflow for continuations/IB siblings. Its alternative HAS_DIRTY_CHILDREN bit does not prune MarkSubtreeDirty. ReflowInput's font-inflation branch uses MarkSubtreeDirty rather than introducing a new parent-only mark. These source paths support the producer premise for ordinary style invalidation.

The concrete direct-only bit publisher found in this bounded audit is the anchor position-try fallback loop in `AbsoluteContainingBlock::ReflowAbsoluteFrame`, immediately before another absolute-frame reflow. No sequence was established that leaves this state as an already-dirty principal ancestor with a clean queried leaf at the candidate's hidden return. Other specialized SVG publishers, initial construction, interrupted/partial reflow, reparenting and callback histories remain unaudited or unproved. The abstract dirty-barrier countermodel must not be reported as a native regression witness.

## Open obligations

1. Derive native entry conditions and preserve the required state projection through actual measurement, final skipped layout and later callbacks; do not assume marking every descendant stays true throughout reflow.
2. Relate the finite stable ownership forest to actual frame child-list topology. The kernel model is recursive; the extracted native helper uses a stack. Arbitrary graph/alias/lifetime equivalence is not proved.
3. Account for placeholder targets outside visited lists, the container's absolute list, other fragments and specialized table/SVG query behavior. Unvisited does not itself mean stale: later absolute/overflow handling can perform additional work.
4. Prove the actual forcing walk reaches and recomputes the same queried frame, with real layout/provider and geometry-observer semantics. Imported direct-query composition remains conditional.
5. Keep source portability/standalone packaging and browser acceptance separate. Root-owned expanded runtime evidence is external to this capsule.

The complete facade contracts are in `capsule/SCOPE.md`. The kernel/compiler binaries are pinned; the complete installed standard libraries, SDK and OS are trusted dependencies. No global native arithmetic or full CSS claim is made.

Development compiler failures/warnings are retained. Initial nested-Tree DecidableEq/termination attempts failed; concrete well-founded evaluation witnesses were rewritten using kernel simplification, and deprecated simp names were corrected. Final canonical/relocated model builds and audit logs are clean. Disposable executables and olean files are removed after retaining source, commands and observations. No production source, index, browser, build or Git state was changed.
