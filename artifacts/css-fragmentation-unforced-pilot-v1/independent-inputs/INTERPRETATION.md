# Independent unforced-break interpretation

This inventory was derived from the primary source before reading importer interpretations. The selected profile is the pinned Editor Draft, SHA `57df3c079bf09547c05c1c0745b1ea1067344e88adaa844ec2e1ed1cde5faa82`, [Unforced Breaks](https://drafts.csswg.org/css-break-3/#unforced-breaks). Thirteen requirement candidates and eight distinguishing abstract scenarios are in the two JSON files. No normative Lean binding or engine conformance claim is accepted yet.

## Proposed contract shape

Use a relation `AdmissibleUnforced input choice`, not a function returning one canonical cut. Keep `input` independently supplied: ordered content identities, fragment extent, candidate positions/class, applicable break kinds and controls, ancestor relations, line counts, decorations, and monolithic status. A chosen cut records its relaxation stage and which decorations were truncated. Its geometry result must come from a layout relation; it cannot be supplied as an expected final answer.

Separate `NecessaryConditionsAtStage` from `FeasibleWithoutOverflow`. Merely passing Rule 1–4 does not prove a complete layout is feasible or that this particular break must occur. Escalation should require a certificate that the previous stage cannot provide sufficient breaks for this input. The meaning of “sufficient” is an expert interpretation/provider boundary; substituting `candidates=[]` loses overflow/placement cases. Do not make all stages unconditionally available.

The finite executable pilot can enumerate a supplied finite opportunity set, filter by necessary conditions, and return a nonempty set of permitted outcomes or a named unresolved geometry dependency. It must not report `Invalid` when the implementation simply lacks the layout provider. A subsequent soundness theorem should connect an executed selector to membership in the independently defined relation, followed by existence for an explicitly inhabited input domain.

## Nonvacuity and progress obligations

Require concrete inhabitants for strict, line-relaxed, avoidance-relaxed, decoration and emergency branches. Also exhibit failed guards. A theorem over a permanently false guard or an empty output set does not close a requirement. The arbitrary-comparison/taint machinery from other CSS components supplies no fragmentation semantics here.

For a finite atomic-content pilot, use a cursor/remaining-token measure and require strictly positive consumption on emergency fragment creation. This is a proposed finite abstraction, not a theorem that nonzero real geometric progress guarantees termination: a real-valued model can make infinitely many positive but shrinking steps. To claim termination, provide a well-founded content/geometry measure and a finite input/fragment-generation contract. Empty content and zero-sized boxes need separate handling; neither authorizes an infinite sequence of empty fragmentainers. Forced blank pages also require their own rules and must not be banned by generalizing the emergency clause.

## External dependency frontier

| Provider | Required interpretation or evidence |
|---|---|
| Break opportunity classification | §4.1 classes A/B/C; layout-mode extensions; monolithic classification and UA choices |
| Applicable break controls | Cascade/computed values; property tables; child-parent propagation; break-kind matching; nested and parallel flows |
| Forced breaks | §4.3 preempts the unforced-choice relation; page side and named-page dependencies |
| Line counts | Inline layout, shaping, line boxes, enclosing-block identity; widows/orphans property validity and small-block behavior |
| Geometry and overflow | Block/inline axes, remaining extent, sizing, floats, margins, fragment placement and varying fragmentainer sizes |
| Decoration slicing | Clone/slice provider and §5 box model; distinguish ordinary margins from cloned decorations |
| Emergency progress | §4 minimum block-size premise, finite content measure, graphic slicing representation |
| Observation | Fragment partition/order, line assignment, decoration geometry and clipping/lost content; CSSOM rectangle/print observer correspondence remains external |
| Optimization dependency | [§4.5 best-breaks](https://drafts.csswg.org/css-break-3/#best-breaks), especially zero-sized-fragment placement; heuristic preferences cannot become exact-output mandates |
| Dynamic execution | Style/DOM/viewport changes must invalidate and recompute appropriate inputs; this section supplies no full host update algorithm |

No table occurs inside the target section. Property tables, break classes and geometry rules are nevertheless dependencies, not accounted-for semantics merely because a hyperlink exists.

## Source hazards requiring explicit disposition

The target range is the heading `unforced-breaks` through the content before the next peer heading `best-breaks`. Its introductory definition, all four definition-list entries and all four fallback paragraphs belong to the range. The nested empty `monolithic-breaking` span is an anchor inside the final paragraph, not an endpoint that truncates the final progress requirement.

Rule 4 displays “class B” but links to `btw-blocks`, the class A definition. The candidate interpretation follows the visible B/C wording and nearby Rule 3 context, while keeping the source-link inconsistency unresolved for expert adjudication. An importer must retain both; successful anchor resolution cannot establish semantic consistency.

The [published 2018 CR](https://www.w3.org/TR/2018/CR-css-break-3-20181204/#unforced-breaks) repeats block-end in its second decoration truncation stage. The selected ED says block-start. PUBLISHED-SOURCE.json retains the dated CR identity. This pilot must not silently rewrite the CR or claim its ED rule proved for both profiles. Likewise, the adjacent mandatory zero-size rule is a named dependency, not silently part of the selected section.

## Acceptance target

First close the reviewed interpretation of these thirteen candidates and their dependency interfaces. Then implement the finite opportunity/filter pilot plus branch inhabitants, forbidden-choice counterexamples and a conditional progress proof. The artifact's value is a reviewable boundary and actionable contract; clause counts are not a denominator for all CSS fragmentation or all CSS.
