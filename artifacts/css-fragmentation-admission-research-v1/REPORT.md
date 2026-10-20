# Fragmentation admission: sufficiency and emergency regions

Research only. The final pilot and independent review remain unchanged. Fresh Editor Draft bytes exactly match the pilot's source SHA `57df3c079bf09547c05c1c0745b1ea1067344e88adaa844ec2e1ed1cde5faa82`. Primary specifications and CSSWG issue bodies/comments are retained under `source/`; fetch and search records identify them. No browser, native build, Git mutation or new Lean proof was performed.

## Decision for the next bridge

| Obligation | Verdict | Safe next action |
| --- | --- | --- |
| “Sufficient” means merely a nonempty allowed-point list | **Refuted** | Include placement geometry and complete alternative decisions |
| General CSS sufficiency is equivalent to current `GridFeasible` | **Unresolved / not derived** | Do not instantiate `SufficiencyCorrespondence` by definition |
| Fixed-geometry ordinary next-placement feasibility | **Precisely definable restricted target** | Derive opportunities and geometry from a small real box domain, then prove a permitted-policy result |
| Exact emergency candidate region for arbitrary flows | **Unresolved** | Preserve both competing interpretations; do not implement a fitting-point filter as settled CSS |
| Emergency region in a single isolated monolithic object, no gaps or siblings | **No internal possible points, subject to actual classification** | A useful narrower optional-slicing policy can avoid the disputed region decision |
| Zero-sized fragment after overflow | **Resolved by current text and CSSWG resolution** | Model it separately from the fitted-zero rule |
| End/start clone truncation order | **Resolved for pinned ED** | Preserve published-version difference and derive active decorations |

The recommended next implementation is the **ordinary next-placement bridge**, with emergency and partial-fragmentainer inputs explicitly dispatched or reported unsupported. This is useful progress, not resolution of whole §4.4.

## 1. Trace and what it establishes

The source sequence is: construct possible points (§4.1); process applicable forced breaks (§4.3); apply ordinary restrictions and ordered relaxation (§4.4); choose a permitted policy (§4.5). Geometry and fragment decorations come from §5. The wording ties relaxation to avoiding overflow and leaves break selection partly discretionary. It does not define an executable universal sufficiency test. [CSS Break3](https://drafts.csswg.org/css-break-3/#unforced-breaks).

The earlier CSS2 algorithm has a similar qualitative trigger with a different relaxation order. It is historical context, not a missing algorithm to splice into the current level. [CSS2 page breaks](https://www.w3.org/TR/CSS2/page.html#allowed-page-breaks).

Consequently, the pilot's theorem `evaluate.isSome ↔ GridFeasible` is sound mathematics about its concrete domain. Calling the right-hand side `specSufficient` would not discharge the interpretation or box-layout provider obligation. The pilot's one-step search also does not prove existence of a complete fragmented history at one fixed relaxation stage.

### A precise useful domain

Start with one normal-flow block formatting context on identical, initially empty fragmentainers of integer CSS-pixel capacity at least one. Use a finite sequence of block-level replaced boxes with known used heights no greater than capacity; no descendants, adjoining margins, borders, padding, floats, relative offsets, percentage sizes, parallel flows, named-page changes or forced controls. Derive the class-A boundary roster from actual sibling occurrences. Explicitly fix the applicable break-control/monolithic policy rather than infer it from serialized declarations. Zero-height boxes may be admitted with their earlier-side rule.

Here define **next-placement sufficiency** as existence of either a fitting completion or a nonempty fitting prefix ending at a permitted boundary, with the required zero-height suffix consumed on the earlier side. Every fragment begins with the whole available capacity, so moving to another identical empty fragmentainer cannot improve geometry. Heights and the complete sibling roster give a concrete constructive route to the pilot's sum and search contracts.

This is a proposed semantics for a restricted next decision. The bridge must still prove actual computed used heights, control propagation, ownership, opportunity completeness and fragment materialization. A source-reviewed permitted-policy theorem is a safer first claim than a biconditional with an undefined general CSS phrase. Full paragraph/text geometry, widows/orphans, stage-dependent re-layout and emergency behavior remain separate extensions. Do not count excluding those inputs as solving them.

## 2. Distinguishing examples

These are interpretation/model tests, not observed engine bugs. `examples.py` executes eight small arithmetic distinctions; it does not certify their CSS admission.

**Legal point beyond capacity.** Two content records have extents 4 and 1, capacity 2, with their ordinary boundary at offset 4. The legal set is nonempty, but it contains no fitting ordinary placement. This refutes “nonempty allowed set = sufficient.” For emergency testing, all future points yields a positive-offset point, whereas limiting points to the current capacity yields none. Both lists meet the pilot's weak subset/bounds premise. That premise cannot choose between them.

**A legal deferral omitted by a local input.** A paragraph has 9 one-unit lines, with 8 units left on the page, `orphans:10` and `widows:20`; the next page has room for the complete paragraph. A paragraph-only input has neither a fitting finish nor a legal internal split, but a preceding class-A break can move it intact. The specification includes this form of example. A lowering that forgets preceding content or a distinct deferral action would falsely treat its local failure as authorization to relax line constraints. [CSS Break example](https://drafts.csswg.org/css-break-3/#widows-orphans-example). The first proposed domain excludes partial occupancy until this decision is represented.

**Zero prefix and zero suffix differ.** `[0,5]` at capacity 2 has a positive cut index after the first item but geometric offset zero. `[2,0,1]` at capacity 2 must account for the zero item on the earlier side; `[4,0,1]` cannot use that same fitted-zero argument after the overflowing first item. The zero fragment's placement rule is now supported by explicit WG decisions, including the after-overflow case. [CSSWG issue1529, first resolution](https://github.com/w3c/csswg-drafts/issues/1529#issuecomment-415098496), [after-overflow resolution](https://github.com/w3c/csswg-drafts/issues/1529#issuecomment-417015453). This resolves the policy oracle, not the provider proof that a native box is the relevant zero-sized fragment.

**Forced completion.** Two one-unit siblings fit capacity 2, but a forced break between them prevents treating “all content fits” as sufficient for finishing. The pilot deliberately lacks a complete dispatcher. Applicable forced values, propagated controls and page-name transitions must be detected before ordinary completion, including required context matching. [Forced breaks](https://drafts.csswg.org/css-break-3/#forced-breaks). A list with forced points removed is not an equivalent input.

**Changing active decorations.** Let a plain sibling of height 1 precede a decorated container with two unit contents. The container has zero start decoration and a two-unit cloned end decoration. At capacity 2, a cut before entering the container has extent 1; a cut after its first content unit has extent 2+2. A constant added decoration of zero falsely admits the latter; a constant two falsely rejects the former. This challenges that *lowering*, not the grid theorem. A correct representation may encode completed decorations into atoms and still needs cut-specific active-clone information, or a proven common active stack for every admitted candidate. It must also distinguish original from cloned edges and normalize adjoining margins before summing. [Fragment decorations](https://drafts.csswg.org/css-break-3/#box-decoration-break).

## 3. Emergency region: useful evidence, no general closure

The text uses possible points, not merely those allowed before relaxation. A guard based on the strict allowed set would forget points that later stages make available. “Below the top” is geometric; neither content index nor the existence of a prior zero-height record suffices. But the inspected text does not explicitly delimit the candidate region as all future-flow points, those geometrically within the current fragmentainer, or a region determined by layout/backtracking. In particular, adding a `y ≤ capacity` filter is an interpretation, not a proved consequence.

CSSWG issue4509 is unusually relevant: its example has an oversized border preceding two lines, placing an ordinary line boundary beyond the column capacity. The discussion accepts slicing/overflow latitude and notes both can be useful; it does not publish an exact candidate-region algorithm. Closing the issue as invalid did not establish the pilot's region equality. [Issue4509](https://github.com/w3c/csswg-drafts/issues/4509), [editor's explanation](https://github.com/w3c/csswg-drafts/issues/4509#issuecomment-553451426).

The distinction between slicing a graphical representation and internally reflowing monolithic content also remains important. Issue6326 discusses that difference, while issue6056 concerns monolithic descendants that overflow. Neither supplies the missing region definition. [Issue6326](https://github.com/w3c/csswg-drafts/issues/6326), [issue6056](https://github.com/w3c/csswg-drafts/issues/6056).

A narrow noncontroversial target is one truly monolithic replaced object, alone at the fragmentainer start, with zero surrounding gaps/decorations and no internal points. Derive the empty possible-point set from that complete box classification. Then optional positive graphical slicing can be modeled as one policy; it is not a required unique outcome. Zero-prefix extensions require actual zero-box placement accounting. Adding a following sibling reintroduces the disputed beyond-capacity boundary, so the isolated-object result must not silently generalize to it.

## 4. Proposed small contract

Uncompiled pseudocode; `Actual*` predicates must be defined independently from box/fragment semantics, not supplied as convenient Booleans.

```lean
inductive NextDecision
  | finish
  | ordinary (cut : BoundaryId)
  | defer (boundary : BoundaryId)
  | forced (event : ForcedEvent)
  | optionalSlice (piece : GraphicPiece)
  | outsideDomain (reason : BoundaryReason)

structure OrdinaryAdmission (s : LayoutState) (i : Fragmentation.Input) where
  wholeFlow : ActualFlowProjection s i.content
  roster : ActualBoundaryRoster s i.opportunities
  noForced : NoApplicableForcedEvent s
  geometry : ∀ stage cut, ActualPrefixExtent s stage cut = extent stage i cut
  zeroPlacement : ActualZeroPlacementCorrespondence s i
  complete : ∀ stage,
    ActualOrdinaryNextPlacementExists s stage ↔ GridFeasible stage i
  materialize : ∀ stage choice, ValidChoice stage i choice →
    ActualPermittedDecision s (decode choice) (materializeFragments s choice)
```

For the first domain, derive these fields from its box constructor and geometry equations. `complete` must quantify all admitted current placement alternatives; the partial-occupancy example shows why hiding a deferral invalidates it. The `materialize` field links the *selected* result to real fragments, not just existence of a different valid placement.

Keep a separate emergency contract containing the **exact region relation**, classification of graphical versus layout content, and policy choice. Until the general region relation is justified, return `outsideDomain` there or use the isolated-object instance. Neither `RegionCandidateAdmitted` nor positivity of an eventual slice supplies this missing relation.

## 5. What can be implemented next

1. Build the restricted ordinary adapter, retaining the full source-to-box correspondence as a named proof task. Test all five distinctions above before extending its domain.
2. Extend the zero-fragment model with an explicit predecessor-overflow state and the issue1529 rule. Do not modify the accepted predecessor capsule.
3. Preserve an emergency-region counterexample contract with both results; do not promote a chosen region into universal CSS admission. An upstream clarification would ask specifically how the oversized-first-item/following-boundary case scopes “possible break points.” No issue has been filed here.
4. For decoration extensions, replace the naive shared-list assumption with a derived active-box stack or candidate-dependent geometry. The ED's end-then-start order is confirmed by issue5070 and the 2015 WG resolution; the fetched published TR still contains the duplicated block-end wording. Keep the ED profile explicit. [Issue5070](https://github.com/w3c/csswg-drafts/issues/5070#issuecomment-633740450), [2015 minutes](https://lists.w3.org/Archives/Public/www-style/2015May/0279.html).

The exact searches and relevant issue comments are retained. One broader phrase search returned 56 results with only the first 30 retrieved, so this is not an exhaustive literature or novelty claim. No relevant retrieved decision closes general sufficiency or the exact emergency region. The narrow ordinary bridge is implementable without pretending otherwise.
