# Rollback cycle test contract audit

The two callbacks in `revert-rule-cycle.tentative.html` are not accepted as two additional browser defects. Their expectation that a rollback cycle resolves to `unset` remains an unsettled specification contract. This audit neither changes their expected results nor changes Firefox to satisfy that expectation.

## Question and scenario

Does the current CSS Cascade specification require the two tentative test cases to discard the base layer and resolve to `unset`?

Both targets have red color, 50px left margin and a red unregistered custom property in a base layer. A later layer supplies `revert-rule !important`; a further layer supplies normal `revert-layer`. The second target adds one more normal rollback layer. The parent supplies green color and custom property, and a 100px margin. Each test callback expects green, 0px, green: inherited values for the inherited properties and the initial value for margin. A failed first assertion prevents that callback's later assertions from running.

The exact checked-in WPT is retained as `reviewed-wpt.html`. Its originating commit is `c93ad286c9bd994048e320d2b8f267e334db085d` (bug 2062624, WPT PR 61852). This is an existing tentative test, not a newly authored reproduction.

## Specification trace

1. The important declaration selects [the rule rollback definition](https://drafts.csswg.org/css-cascade-5/#revert-rule-keyword). The deciding text says the value is calculated:

   > as if the current style rule had not been present at all.

2. Reconsidering the remaining declarations encounters [layer rollback](https://drafts.csswg.org/css-cascade-5/#revert-layer). Its prose removes the current layer and the interval between its normal and important positions. It does not explicitly state how earlier rule exclusions survive this reconsideration, or prescribe a cycle-detection fallback.

3. [The definition of unset](https://drafts.csswg.org/css-cascade-5/#valdef-all-unset) supplies the inherited/initial behavior asserted by the test, but does not establish that these scenarios must select that keyword.

The missing transition is from mixed rule/layer rollback to cycle resolution. Under a persistent-exclusion interpretation, the removed rule stays absent and rollback can reach the base declarations. Under a restart that forgets exclusions and revisits stronger declarations, a cycle is possible. Those are interpretations illustrating the missing contract, not newly proved normative algorithms.

**Verdict: INCONCLUSIVE** — the captured specification does not settle the test's cycle-to-unset expectation, and the relevant CSSWG discussion remains open.

| Candidate reasoning | Assessment |
| --- | --- |
| A tentative WPT expects unset, so this is a normative requirement | The test is evidence of a proposed behavior, not a specification resolution. |
| No indexed step route reaches unset, so unset is forbidden | Invalid inference: these definitions are prose, not a complete indexed algorithm. |
| Persistent exclusions avoid revisiting the removed rule | A plausible reading, also mentioned by the CSSWG issue; it does not independently settle the specification. |

## Current primary-source evidence

[CSSWG issue 13916](https://github.com/w3c/csswg-drafts/issues/13916) was open in the November 10, 2026 capture, last updated May 13, with three comments. The issue discusses permanently ignoring reverted rules versus restricting rollback to weaker declarations. Another proposal treats rule rollback as a sublayer, with disagreement about important conditional fallbacks. Neither the issue nor its captured comments adopts a cycle-to-unset rule. The issue's example crosses origins, whereas this WPT crosses layers; it addresses the shared rollback-direction ambiguity, not an exact normative answer for this fixture.

`PRIMARY-SOURCES.json` records URLs, retrieval time and hashes for the full specification and complete issue/comment response. The three specification query outputs have the same HTML hash as the independently downloaded specification. `anchor-validation.json` records successful validation of all three specification anchors used above. The valid depth-18 step trace has zero routes; it is retained only as a tool limitation, not proof of non-reachability. Earlier failed discovery commands and the trace using the invalid `#unset` endpoint are retained and superseded by `unset-definition.md` and `unset-trace-valid.md`.

`AUTHENTICATION.json` pins the Firefox revision and proves the retained WPT equals both the working file and its committed bytes. No browser run occurred in this audit. The prior same-rule validation's five passing/two failing control signature remains historical evidence; the two failures were already retained before this audit. The phrase “manifestations of the existing same-rule lead” in `css-revert-rule-production-validation-v1/DECISION.md` should not be read as a settled additional bug claim.

## Delivery consequence

Keep the two tentative failures separate from accepted regression tests and from the 169-entry repair catalogue. Do not weaken or rewrite the tests merely to make a local suite green. Revisit when the CSSWG resolves the rollback contract or when a native crash/nontermination reproducer supplies an independent defect. Existing #163/#164 fixes and their proved cumulative-exclusion model retain their documented scope; this audit does not prove that every assumption in that model follows mechanically from the specification.
