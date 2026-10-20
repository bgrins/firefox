# Source correspondence and admissions

## Bound implementation

`source/before.cpp` and `source/candidate.cpp` are the complete immutable root snapshots, externally pinned before copying. The source extractor selects the complete `ScrollContainerFrame::GetNaturalBaselineBOffset` method from each. `source/ReflowInput.h` is the complete identified local header; Searchfox discovery located `CSSMinMax`, and its complete template is extracted and compiled unchanged. Balanced lexical extraction supports these ordinary definitions, not arbitrary C++ syntax or automatic translation correctness.

The candidate method is copied unchanged into the extracted harness. The actual `CSSMinMax` template is also copied unchanged. The class, Maybe/map, query, writing-mode object, scrolled child, style display, geometry and fallback methods are synthetic adapters. Their calls and arguments are observed; this is not a build of Gecko's frame implementation. The original method is separately compiled, not reconstructed from the candidate.

## Universal mathematical joins

* `Provider.lean` is the unchanged fourteen-result root draft. Source/version transfer is recorded; these results are inherited, not fourteen newly discovered claims.
* `Dispatch.continuation` follows the actual containment/Option/map/first-or-last conversion. `native` follows the legacy LineLayout/Last/query/nonbutton branch before it. No geometry query is executed when the selected child answer is absent.
* `route` classifies the independently stated legacy/suppressed/absent/delegated contract. `physicalBaseline` reconstructs a block-start point and uses explicit before/inside/after cases. `full_value_refinement` proves agreement for nonnegative outer extent. It does not assume the desired output.
* `expectedCalls` derives represented calls from that classified outcome. `exact_ordered_calls` connects the source-shaped branching to this sequence. The trace observes provider methods, not every C++ load, accessor, allocation or compiler operation. Argument forwarding is checked in extracted execution; universal writing-mode representation refinement remains external.
* `sourceClamp` follows the two assignments in actual CSSMinMax. `native_primitive_is_clamp` derives its max/min meaning for arbitrary integer bounds.
* `all_candidate_operations_fit` admits nonnegative, signed-int32-representable inner/outer extents, an arbitrary signed-int32 border and child baseline. It proves both int64 intermediates, the clamped narrowing and final int32 subtraction. The method's legacy synthesized result bypasses clamping: its provider must itself return a representable nscoord. The method has no array or heap allocation to bound.
* `none_iff_no_selected_provider`, the zero witness and preserved nondelegated outputs distinguish absence from numeric zero. First-group complete output preservation is universal in the model. No equality of inner and outer extent is assumed.

## Remaining real provider/caller obligations

1. The scrolled frame is nonnull and stable for the call; query classification, button state, containment, child baseline, logical sizes and borders describe the same frame state. No reentrant provider, mutation or destruction is modeled.
2. For a delegated child answer, first means distance from its block-start, last means distance from its block-end, measured in the requested compatible writing mode. The child's padding is already included. Logical sizes and border-start translation must describe the actual frame coordinate origin. Scroll offset is deliberately not inserted by this component; actual provider alignment/scroll-position semantics remain a caller/source obligation.
3. Actual frame geometry establishes nonnegative representable sizes. The model proves consequences of those numeric premises; it does not derive all Gecko frame-size invariants. It accepts signed borders for arithmetic safety although normal used border widths are more restricted.
4. Legacy block LineLayout synthesis, layout containment classification and child natural-baseline truth remain provider obligations. Preserving their dispatch does not prove their CSS conformance.
5. Native nscoord/int64 widths, Maybe/map semantics, C++ integer promotion, compiler, runtime, heap availability and lifetime are admitted. The exact extracted execution is finite evidence for the selected operations. Lean's Init/Std and library/runtime are trusted dependencies beyond the pinned Lean executable; the checker does not hash their entire inventory.
6. No whole Flexbox donor selection, normal-position lifecycle, frame publication, parent baseline alignment, fragmentation, pushed-item readiness, F11/F12 closure or dynamic browser history theorem follows.

The reference conversion is motivated by the baseline export context in [CSS Align 3](https://drafts.csswg.org/css-align-3/#baseline-export), freshly checked during preparation. Retained primary excerpts and root source trace are contextual evidence. The proof is a conditional coordinate/dispatch component, not an automatic formalization of that entire section.

## Finite execution boundary

1536 inputs independently reconstructed from all 32 Boolean guard combinations, three forwarded writing-mode identities and sixteen geometry/absence choices. Numeric choices cover unequal extents, both asymmetric borders, all clamp regions, zero outer/inner, zero answer, absence, signed border, and int32 extrema. Three mode identities test argument forwarding; they do not implement full WritingMode geometry.

Candidate runs all 1536 cases in debug, release and UBSan and agrees with Lean and a separate Python physical-coordinate oracle, including ordered calls. Original runs 1446: the remaining 90 contain a delegated border-plus-baseline sum outside signed int32. The wrapper emits explicit SKIP rows before invoking original on those inputs. No claim of original UB execution safety or original exhaustive agreement on those cases is made. Original guard paths with the same extreme unused payloads still run safely.

Eight compiled source-method mutants produce intended observation differences (seven also change numeric/presence results); an additional lost-widening source mutation is rejected by UBSan for signed subtraction overflow. The query-inner-for-first mutant is intentionally an extra-provider-call counterexample, not a numerical one. Six kernel-compiled semantic witnesses distinguish model shortcuts and their false equalities are rejected.
