# Infinite value does not establish the step

The current `CalcNode::simplify_and_sort_direct_children` replaces Round with its infinite value after checking only whether the step is a zero or infinite leaf. Both predicates return false for a nonleaf. The replacement therefore discards unresolved step information. The signed current generic source is `df7e69322b099aefed14dd6876a3e634ff4133f25161b99bd93bf8fc1f0c0e16`; source excerpts and hashes are recorded separately. Searchfox independently locates the same shortcut, but the exact changed local body controls this review.

This is an existing unresolved boundary, not a new discovery or fix count. The prior special-knowledge audit explicitly modeled it, and the old 224-observation diagnostic included its 16 contextual-step discrepancies. Accepted 144 guarded the opposite infinite-step branch. Accepted 145 changed finite runtime arithmetic; neither changes this shortcut.

## Necessary knowledge and decisive cases

A syntactic `step.as_leaf()` guard is insufficient. `NaN` is a leaf and reaches the same shortcut. A `1em` leaf exposes coefficient 1 through `unitless_value`, while `canonical_value` correctly reports that the resolved numeric value is unavailable. At font size zero its step is zero. The distinction is already represented by the existing trait; no type whitelist is needed.

Within this shortcut, a sufficient discard condition is a known canonical finite nonzero step. An unknown step must remain attached. A known NaN, zero or infinite step must yield NaN, rather than returning the infinite value; retaining the operation for the existing runtime special-value handling is also a possible implementation route. This is a scoped knowledge condition, not a proof of every other special-value shortcut or context-dependent leaf transformation.

The probe observes `calc(0.5 + 0.25 * sign(round(mode, value, step)))` for all four modes and both infinity signs:

| Case | Font sequence | Expected positive / negative infinity observations |
|---|---|---|
| Scalar infinity, NaN step | 8, 0, 8 | 0, 0, 0 for either sign |
| Infinity times 1px, 1em step | 8, 0, 8 | .75, 0, .75 / .25, 0, .25 |
| Infinity times 1px, fixed 8px step | 8, 0, 8 | .75 throughout / .25 throughout |

`observation.js` holds the declaration through the three font changes, records all 72 snapshots, and removes its iframe in `finally`. It checks support, specified serialization, repeated computed reads, direct NaN encoding, actual font/1em width, and literal expectations. The resolved Round expression is diagnostic: the same literal-NaN bug can affect it. It is not a successful calibration by assumption. The return detaches shared calibration objects through JSON serialization because the first root MCP capture lost repeated object references; that initial incomplete capture remains preserved by root.

## Existing evidence and test overlap

Root executed both diagnostics in **system Firefox 158**, not the locally built branch. Independent `analyze.py` replay validates exact rosters and direct calibrations. The 224-record diagnostic has 53 discrepancies, including the known 16 infinite/contextual-step cases. Its resolved-Round diagnostics also have 24 discrepancies, separately recorded. The detached new 72-record capture has 24 NaN-step discrepancies and eight relative-leaf discrepancies at font zero; all fixed-finite controls and direct calibrations pass. These are observation counts, not independent bugs or local candidate results.

The accepted infinite-step page has 23 cases about unresolved values, finite sign changes, and integer controls. Its literal both-infinite control does not cover an unknown step, NaN step, or zero-basis relative step. Retain it as a preservation control. The existing `RoundSpecialKnowledge.infinite_value_retained_iff` and `unresolved_step_no_constant` already express why an unresolved step cannot be replaced by one constant; `nan_priority` covers NaN. The unchanged original `Knowledge.lean` and `model_check.py` were replayed: all four laws pass with `propext` only, and four false controls are rejected. Owned compiler products were removed. No new theorem, canonical coverage, or native refinement is claimed.

## Candidate review

The author's six-line addition in `css-round-infinite-value-repair-v1/native.patch` obtains the step's canonical numeric value, retains unknown steps, and coerces the result to NaN for a known nonfinite or zero step. This addresses the reviewed shortcut without altering finite rounding or the accepted infinite-step guard. Candidate source SHA is `b91a35a7ff908fed8dd20312d840149f00503b17465aa2ffc1cb79a8cbfb55d4`.

The 32-case proposed WPT combines four modes, two value signs, and four families: contextual square-root NaN/zero, contextual reciprocal infinity, zero-basis relative leaves, and literal NaN/zero/infinity/finite classes. The finite-step controls and independent literal/direct-input checks have coherent oracles. The separate eight-consumer diagnostic records support, setter output, computed output, literals, direct contextual controls, and font recovery. This is bounded source/test review, not compilation or candidate execution; the admission hold below remains.

## Admission remains a separate obligation

The old shortcut can erase all context before an enclosing `sign`, allowing a constant result into context-free easing consumers. Retention can expose that context and cause rejection. Test a strictly positive contextual step such as `2 + sign(1em - 16px)`: its mathematical result is always the same infinity, yet the implementation lacks that range proof. Use ordinary z-index/grid computation controls alongside steps, cubic-bezier and linear admission/evaluation diagnostics. Do not infer ordinary-repeat rejection from the historical subgrid guard: current accepted subgrid support differs, and the old policy audit already corrected that mistake.

Passing opacity cases alone is insufficient for unrestricted native acceptance. The candidate needs explicit consumer-policy handling or an honestly bounded hold. No source edits, build, browser execution, index changes, or acceptance occurred in this review.
