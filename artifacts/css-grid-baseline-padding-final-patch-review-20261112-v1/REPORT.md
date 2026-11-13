# Final proposed patch and WPT source review

The three-file native change matches the reviewed fix design. The WPT snapshot has one blocking harness error and lacks the requested parent-reset phase. This review pins the specific candidate bytes copied under reviewed/, rather than future edits to the root-owned working capsule. No compiler or browser was run here.

## Blocking WPT issue

The test calls `promise_setup(() => document.fonts.load(...))` and then registers synchronous `test(...)` cases. Testharness explicitly rejects `test` after `promise_setup`, sets harness ERROR and completes the run. The exact indexed implementation is retained in testharness-test.txt. A normal list of subtest-looking results must not substitute for a successful harness result.

Use `promise_test(async t => { ... })` for these cases so the callbacks follow successful promise setup. Their individual body need not await anything: the geometry reads intentionally flush after each edit. Alternatively load the font in a properly structured asynchronous test sequence, but do not remove font readiness and then interpret fallback-font geometry as the Ahem expectation. Root was notified before completing this review.

## Native change

PresShell sets PaddingIncludesBaseline only in the non-root branch supplying current used padding. CallerWillInit prevents initialization before that point. It removes the bit immediately after Init, keeping the new provenance signal local to this acquisition operation. No frame-global persistent state or baseline property is changed.

InitOffsets initializes a local false boolean and sets it only in the selected explicit aPadding branch. The earlier theme and SVG cases do not inherit this suppression. The lambda guards only the numeric addition: property presence, sign/side selection, cache need and block relative-size marking remain unchanged. The existing IsGridMeasuringReflow and ShrinkWrap guards remain unchanged. Consequently raw overrides without the flag, absent overrides, and overridden-by-theme/SVG acquisitions retain their old path.

The original child constructor initializes mComputeSizeFlags from its explicit argument; it does not copy that member from the parent with mFlags. The extra post-Init removal further limits accidental use during child reflow. Appending an enum member changes later enum ordinals, but these are in-process EnumSet flags; source/build review should still reject any external serialization or ordinal assumption if encountered. No such dependency was found in the earlier indexed member inventory. Source semantics do not replace the root's whole native compile gate.

Preserving needPaddingProp even for an already-resolved record keeps baseline-driven property retention; preserving the state-bit operation matters because InitResizeFlags runs after InitConstraints and reads the bit before potentially clearing it for a dirty frame. The patch correctly avoids relying solely on historical state.

## Assertions and missing coverage

The loops define 120 cases: five containment choices, first/last alignment, three writing modes, two directions and two peer sizes. Each changes one same-font line from X to XX and back in a fixed 100-pixel inline-size box, without wrapping. This should change inline extent, not the line's block metrics. Ahem loading must complete first. Testing the content's block-axis offset relative to the target avoids dependence on document placement. The helper selects top for horizontal-tb, right for vertical-rl and left for vertical-lr; direction changes inline progression, so those block-start selections are appropriate. The writing mode is shared by grid and descendants; these are not orthogonal-parent/child tests.

The target has explicit content-box block-size 100px and no box-sizing override, so the content-size assertion is meaningful. Border-box dimensions and relative content offset are compared with the initially flushed layout. Exact equality is reasonable for these stable integer Ahem metrics and unchanged geometry; this is not a general floating-tolerance claim. Tests fail fast, so the number of planned assertions is not evidence every assertion ran on an unfixed browser.

There is no parent-driven reset/change in the reviewed WPT: only the descendant text changes. Add a phase that changes the parent alignment/peer metrics and/or target padding, flushes, then compares that new result with a fresh equivalent clone and performs another child edit. The expected offset for this phase must be the fresh equivalent result, not the original pre-change offset. This distinguishes a correct snapshot provenance flag from accidentally suppressing a newly required baseline contribution or leaving stale cached values. Include a transition removing and reinstating baseline alignment if feasible.

A nested baseline-bearing descendant/raw-override case and orthogonal writing modes would strengthen coverage of noninheritance/axis selection. Theme/SVG-precedence and measuring/shrink-wrap branches may require targeted native/source coverage if ordinary browser fixtures cannot reliably exercise them. The reviewed native patch preserves them textually, but this WPT does not independently validate every such branch.

## Evidence boundary

Authentication command 7c8a9c matched all three original/candidate native pairs and the candidate WPT against INPUTS.json. The exact patch is retained. Native candidate ReflowInput.cpp SHA is c731df12591db3534715a5e827cea38ea3116df2ec6c74539fc8b83d2fbb798a; reviewed WPT SHA is 3331e7d294d9d65b2a8f50f43a80fddf9e36e0e16f8b57c703f8e41d543b1483. Earlier frozen source review and browser probe remain separate evidence. No repaired-browser success is claimed here.

The focused repair does not resolve signed32 padding/border composition overflow or the wider exact geometry project. Those targets and all remaining consumers stay in scope separately.
