# Hidden absolute-child sequence: scoped formal companion

## Result

The selected pre-input invalidation has a kernel-checked explanation for the clean-hidden-zero failure and direct/conditionally reachable leaf query recovery. It does **not** prove complete absolute layout or native acceptance. The companion preserves the existing conditional subtree coverage contract instead of assuming every descendant is marked.

The selected three-line native proposal is `candidate-v2.patch`, SHA `d5f61ccd4db2871e17e96e5d84cc30dcb59ad92ac3574878d3169cc1999acdf3`, from the externally confirmed immutable producer `css-hidden-flex-oof-review-v1`, FILES `4571c5fd5131906fb0bb34a1c5a40c981d40d1ab926edbfaa4be488224cb0d24`. The candidate C++ SHA is `926858026128b2934df41c6ec3953b76fb84d2ed66796523b553fc8dcf2373c7`. The superseded after-input variant is modeled only as a diagnostic timing alternative.

## What is proved

The new `OOF` module has 23 theorems. The exact unchanged `Hidden` and `Subtree` modules contribute 66 imported results, counted separately.

- With a stable false hidden predicate, selected-call behavior is unchanged for arbitrary callback and placement providers.
- With the selected true predicate, the root is directly dirty before the dirty-sensitive input flag is computed. The modeled native IResize assignment consequently returns false.
- For the noncontinuation hidden block early-return branch, output dimensions remain zero under the overflow-helper footprint admission. Existing placement and SetRect still publish those dimensions; marking does not immediately publish the real geometry.
- Hidden DidReflow retains the marked bits. The root is query-eligible. A represented descendant is eligible when the original path has no obstructing dirty/table barrier, and preexisting eligibility is preserved.
- Every-bit coverage is exactly the imported root-closure condition. A dirty parent with a clean leaf remains a counterexample to unconditional coverage.
- Selected-leaf recovery composes with the earlier query model and an arbitrary actual returned-size provider. It proves recovery to that provider result, not a separate derivation of CSS dimensions or position.

Concrete appunit witnesses distinguish the old clean zero rectangle `(6600,600,0,0)` from the specified-size centered rectangle `(6240,600,720,480)`. These values describe a small horizontal positioning facade. Full absolute positioning is not extracted or proved.

## Timing and continuation boundaries

The pre-input and late-input variants differ when a clean hidden frame's size differs: the late variant computes IResize as true before marking, whereas the selected variant computes false. An arbitrary non-skipping provider can distinguish that flag and return different geometry. This is a source-level timing countermodel, **not a browser-reproduced regression or proof of a particular native provider response**.

The actual hidden block branch also tests for no next continuation. For a next-continuation call, Lean leaves callback tree/size behavior arbitrary. An explicit callback that clears bits refutes universal post-call eligibility. Executable rows use a stable size-returning provider for that branch, which is a calibration choice, not evidence that all real continuation callbacks have that behavior.

## Source correspondence

The capsule binds 25 complete units or exact statement/branch slices. Complete large units are retained for inspection; binding a unit is not executing it.

| Actual source | Executed/model relation |
| --- | --- |
| Selected `ReflowAbsoluteFrame` | Complete before/after methods bound; selected mark precedes exact RI construction, virtual call, SetRect and DidReflow statements. Intervening sizing/placement/fallback code is supplied by a restricted facade. |
| `GetInFlowParent` | Complete native body executes. OOF lookup uses supplied valid first-continuation placeholder; physical owner is independently varied. |
| Hidden predicates | Complete native bodies execute, including anonymous-box exception and forcing-set lookup. |
| `MarkSubtreeDirty` | Complete stack walk executes; separate Lean recursion retains root/descendant barrier distinctions. |
| `InitResizeFlags` | Complete method bound; only exact dirty-sensitive IResize assignment executes with independently supplied size-difference input. |
| `ReflowOutput` / `LogicalSize` constructors | Complete constructor chain bound through zero initialization; small facade mirrors size initialization. |
| `nsBlockFrame::Reflow` | Complete method bound; exact initial hidden/noncontinuation branch executes. Other layout is a provider. |
| `FinishAndStoreOverflow` | Overload and complete implementation bound; facade is a no-op. Actual property, transform, temporary-size and observer effects are not proved harmless in arbitrary histories. |
| `DidReflow` | Complete method bound; hidden early return and visible state-clearing statement execute. Other observers and flags are not simulated. |
| `UpdateHiddenContentInForcedLayout` | Complete method executes, including dirty gate and in-flow ancestor walk. Scheduling is a counter-only provider. No actual forced reflow/flush executes. |

Sources have explicit roles: the selected absolute caller comes from the sealed OOF proposal; frame/PresShell sources and imported proofs come from the sealed subtree companion; RI/output/writing-mode/inline headers and block source are additional local snapshots. They are individually pinned, not asserted to be one complete tested browser revision. Discovery of constructor/helper locations used Searchfox; local retained bytes define these bindings.

The model reuses a stable hidden predicate across marking, callback entry and DidReflow. Stable identity, style/forcing state, frame ownership, valid placeholder/property decoding and no reentrant graph mutation are explicit premises. Hypothetical independent owner visibility in the corpus tests getter selection; it does not establish that an ordinary DOM box escapes a hidden ancestor's layout-containment containing block.

## Replay evidence

Canonical and relocated closed-capsule runs are retained separately. Each successful run checks:

- 89 exact theorem names and axiom reports: 23 new, 66 imported; only standard `propext`, `Classical.choice`, and `Quot.sound` permitted.
- 6144 independently generated Lean rows against extracted-source facade execution at O0 and O2 with UBSan: 12288 nonmutant row comparisons per replay.
- Eight compiled semantic mutants at both optimization levels: omission, root-only marking, physical-owner lookup, anonymous-exception removal, hidden dirty clearing, continuation skipping, clean-query forcing, and late marking. Each must produce a concrete differing row; compile failure does not count as detection.
- Four deliberately false Lean claims: equivalent timing, unconditional barrier-leaf coverage, immediate nonzero publication, and universal continuation eligibility.

Fifteen integrity controls separately challenge isolation, optimization, payload/hash/role/binding substitution, extra files and caches including resealed inputs, imported-model mutation, proof escape, nonregular input, and output overlap/existence. The closed roster is authenticated before importing the extractor. Tools are pinned; installed SDK and Lean libraries remain trusted external dependencies.

The first development Lean attempt failed because grouped structure fields lacked the required field syntax; its log is retained. The corrected development compile and both sealed replays succeed. Native/Lean compiler products are removed; raw source, outputs, commands and counterexample receipts remain. No main source, browser, build, index or Git mutation was performed.

## Remaining native gates

This is the OOF-specific sequence companion requested for the proposed repair. It does not discharge arbitrary dirty-publisher history, placeholder/OOF ownership closure, fragmentation and anchor retries, all virtual callbacks, actual RI arithmetic, overflow observers, all placement operations, or complete forced-layout traversal. Root-owned paired browser evidence and independent review decide native acceptance separately. The original principal-child proof remains unchanged and is not imported as a runtime prerequisite for this selected absolute-caller change.

Replay: `python3 -I -S capsule/replay.py --manifest-sha 39401a7bfe598270b1eb664182a0ff00eb5904bed7608ab68938a86294b5a363 --out /absolute/fresh/output`.

Outer verification: `python3 -I -S verify.py --manifest-sha <outer FILES hash>`.
