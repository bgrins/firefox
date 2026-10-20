# Whole CSS in Lean: test the composition boundary next

Research memo, 19 October 2026 local time. No new proof, native refinement or browser result. The interface below is **uncompiled pseudocode**.

## Assessment

Covering all CSS is a feasible research objective to pursue incrementally, but the existing results do not yet establish that the architecture scales to whole rendering. The immediate uncertainty is whether separately correct components can share faithful inputs, identities, continuations and observations without assuming the important CSS behavior at their boundaries. Adding more local theorems will not answer that question.

Keep three deliverables distinct:

- **Normative semantics:** model the permitted outcomes and histories of every requirement in a versioned CSS corpus, including normative host dependencies and unresolved interpretation decisions.
- **Executable reference:** implement a permitted policy and prove soundness plus domain-specific availability/progress. It need not reproduce every permitted UA choice.
- **Gecko refinement:** prove concrete state/source representations and observable native histories implement those semantics. Extracted functions, matching hashes and finite browser agreement do not provide that theorem.

“All CSS” must eventually include parsing and recovery, property families, layout, text, fonts, fragmentation, painting, APIs, resources and time across the selected conformance roles/media. Restricting an experiment is useful; treating its restrictions as the eventual definition of CSS is not. An unspecified rule and an unimplemented rule must remain distinct ledger states.

## What changed since architecture v5

The new fragmentation pilot gives a concrete place to test the proposal. `Placement.grid_evaluator_iff` proves equivalence to `GridFeasible`; `Selection.scan_certificate` derives infeasibility of preceding stages. These are useful results, but `SufficiencyCorrespondence` remains uninstantiated. Inputs already contain laid-out atoms, opportunity classes, ancestry, line identities and geometry. The pilot therefore cannot establish that its stage escalation is CSS escalation merely by being joined to a stylesheet parser.

Its retained counterexamples identify actual interface requirements: a positive content index can still have zero geometric offset, and two supplied emergency regions satisfying weak bounds can produce different decisions. The same decoration list must also be valid at every candidate, not reconstructed after choosing a favorable cut. These issues are more informative than an additional generic provider protocol.

The current library supplies reusable local composition patterns:

| Inspected implementation | Reuse | What it does not supply |
| --- | --- | --- |
| `Style.compute_sound`, `GenericStyle` | Matcher → candidates → winner → property defaulting | A complete computed-style record, box tree or host snapshot |
| `CssSourceScopeCorrespondence.parseBody_iff` | Recursive source parser and independent accepted/stopped relation | All CSS contexts, dynamic acquisition or layout |
| `Variables.substitute_spec` / `Substitutes.result` | Substitution against a supplied environment | Correct construction and persistence of the complete environment |
| `CssFiniteScalar.Scalar` | Exact rational value plus signed-zero representation | General rendering numerics, rounding bounds or branch preservation |
| `TransitionMachine.run_iff` | Finite execution from a supplied single-step correspondence | Actual rendering phases, resource consistency or temporal progress |
| Fragmentation `Placement` / `Selection` | Concrete grid decisions and conditional progress | Real opportunity construction, sufficiency, emergency-region admission |

The current roadmap includes considerably broader source/cascade/value work than these representative files. Its coverage map still distinguishes scoped models, finite engine evidence and open layout/host families. No module or audit count is an all-CSS coverage measure.

## Strongest remaining architectural obstacles

**1. Ownership across trees and value stages.** Establish explicit relations from DOM/flat-tree subjects to inherited styles, generated/anonymous boxes, text ranges and fragments. These are not a shared integer ID space. Style output must preserve dependency/provenance information needed downstream; serializing values is insufficient. The box constructor owns this mapping, including omission/splitting rules, rather than having every consumer assume a correct map. [CSS Display box generation](https://drafts.csswg.org/css-display-3/#box-generation).

**2. Layout inputs are mutually constrained.** A text width oracle hides shaping boundaries, line opportunities and source-range identity. Style, inline construction and font selection must generate a shaping request; its response then participates in line formation and fragmentation. CSS Text both forbids some boundary breaks and requires others, so independent per-element shaping is not an adequate general interface. Font bytes and device facts may be external inputs; CSS-facing selection, boundary rules, fallback and invalidation remain obligations. [CSS Text boundary shaping](https://drafts.csswg.org/css-text-3/#boundary-shaping).

**3. Progress is not one global decreasing number.** Finite syntax traversal, finite layout search, emergency slicing and an indefinitely interactive document need different arguments. The pilot proves a Nat-grid slice measure for admitted steps, not existence of a complete CSS layout. Positive real progress alone permits an infinite sequence. A complete architecture needs per-family well-founded measures or a specified bounded phase protocol, and explicit resource-wait states. Fuel exhaustion cannot mean invalid CSS. The fragmentation rules allow choices and relaxation; they do not prescribe the pilot's unique source-order selector. [CSS Break rules and optimization](https://drafts.csswg.org/css-break-3/#unforced-breaks).

**4. Numeric approximation can alter topology.** A small advance error can change a line break, then a page break and every subsequent rectangle. A uniform final pixel epsilon cannot establish the same discrete decisions. Use exact quantities in the normative relation where appropriate, separately model implementation arithmetic, and prove branch agreement away from thresholds or membership in explicitly permitted outcomes at them. Do not silently change Nat-grid proofs into arbitrary real-valued layout proofs.

**5. One observation cannot certify another.** A fragment list needs distinct projections for painting, hit testing, selection and CSSOM. `getClientRects()` observes ordered fragments, including zero-width/height ones, and applies transforms; a total bounding rectangle loses this information. Conversely, equal rectangles say nothing about glyph shape, color, clipping or provenance-dependent URL eligibility. A display-list theorem is a useful intermediate result, not whole rasterization correctness. [CSSOM View rectangles](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects).

**6. Cycles need specified phase semantics.** Imports and custom-property cycles, intrinsic sizing dependencies, container/query effects and scroll-driven animations do not share one generic fixed-point rule. In particular, the scroll-animation draft has a bounded additional stale-timeline update and permits later resampling to be deferred; forced style reads do not invoke that additional procedure. An “iterate until stable” renderer would erase observable timing. The host owns persistent resource/choice histories and permitted sampling phases. [Scroll Animations event-loop integration](https://drafts.csswg.org/scroll-animations-1/#event-loop).

These interfaces must remain relations where CSS permits alternatives. Give each policy a persistent witness and prove that some admitted execution exists. Merely making every output legal—or requiring an impossible admission—would make a soundness theorem useless.

## Concrete next interface

Proposed **uncompiled** adapter from real flow construction to the existing grid pilot:

```lean
-- Snapshot includes styles, box occurrences, shaped runs, resource versions.
-- Continuation includes source ranges, enclosing blocks and consumed content.
inductive Prepared where
  | unforced (input : Fragmentation.Input)
  | forced (break : ForcedBreak)
  | waiting (request : ResourceRequest)
  | unsupported (reason : DomainBoundary)

-- OPEN definitions, not axioms or Boolean labels supplied by the caller:
-- BuildsFlow snapshot cursor flow
-- CompleteOpportunities flow input
-- GeometryCorresponds flow input
-- PermittedPlacement snapshot cursor stage fragments next
-- AccountsForContent flow fragments next
-- RectObservation snapshot fragments replies

structure UnforcedBridge (snapshot : Snapshot) (cursor : Continuation)
    (flow : Flow) (input : Fragmentation.Input) where
  constructed : BuildsFlow snapshot cursor flow
  opportunities : CompleteOpportunities flow input
  geometry : GeometryCorresponds flow input
  materialize : Fragmentation.Choice → List Fragment × Continuation
  selected : ∀ stage choice,
    Fragmentation.ValidChoice stage input choice →
      PermittedPlacement snapshot cursor stage
        (materialize choice).1 (materialize choice).2 ∧
      AccountsForContent flow (materialize choice).1 (materialize choice).2
  placement : ∀ stage,
    Fragmentation.GridFeasible stage input ↔
      ∃ fragments next,
        PermittedPlacement snapshot cursor stage fragments next ∧
        AccountsForContent flow fragments next
```

`prepare : Snapshot → Continuation → Prepared` must derive these certificates in its supported domain. Returning `unforced` also needs a proof that the complete flow has no pending forced dispatch; filtering out forced entries is insufficient. `CompleteOpportunities` must derive class, order, ancestry and current-block line counts from the actual flow. `GeometryCorresponds` must justify all candidate extents and decoration behavior. The independent `PermittedPlacement` relation must not be defined as `GridFeasible` with renamed fields.

The selected-choice clause ties the actual returned cut to its materialized fragments; existence of some legal placement alone would not prove that connection. The first composition theorem should turn `scan_certificate` plus a *constructed* bridge into a permitted fragment result with all earlier stages infeasible in that same semantic domain. A second theorem should derive CSSOM replies from those fragments while retaining element/source ownership. Font/shaping admission remains visibly conditional until its own provider is implemented. Emergency-region correspondence must be separately proved or the adapter must return a boundary for those inputs; a positive progress lemma cannot discharge it.

Import structure remains acyclic: source/style → flow construction → admitted text/geometry → fragmentation → scene/API projections. Feedback executes through a host-step relation between snapshots. This is a semantic dependency arrangement, not a claim that layout can always be implemented as one forward pass.

## Three falsifiable integration experiments

### 1. Construct the pilot's inputs instead of supplying them — next milestone

Implement a finite block/inline domain with explicit breaks, zero-extent boxes, nested block identities, positive widows/orphans, supported decorations and fixed grid metrics. Compute styles for the relevant properties, construct boxes and line records, then derive every opportunity and continuation. Begin with fixed admitted font metrics; record the unproved shaping contract rather than calling it a font implementation.

**Pass criteria:** establish the bridge above for the declared domain; derive line-count partition across actual continuations; account for all source content; prove a terminating ordinary-layout reference where the domain guarantees ordinary placement. Independently reviewed cases must reject wrong-block line counting, omitted opportunities, a positive-index/zero-offset confusion, and prematurely relaxed avoidance. Include a boundary case that returns unsupported rather than inventing emergency sufficiency. The milestone fails if correctness still requires the caller to provide the intended opportunities or `SufficiencyCorrespondence` unchanged.

This closes one specific cross-family gap. Forced dispatch, variable geometry, floats, parallel flows, negative margins, broader text and the emergency ambiguity remain queued whole-CSS obligations.

### 2. One fragment representation, two genuinely different consumers

Use the generated fragments for both ordered CSSOM rectangles and a restricted paint scene (background/border and positioned glyph runs). Include a split inline, a zero-size fragment and a transform; keep broader compositing/rasterization outside the experiment.

**Pass criteria:** independently stated observation relations for both consumers; same source/box/fragment identities; reject a mutant that drops a zero fragment even if the bounding rectangle is unchanged, and one that preserves geometry but substitutes the wrong glyph run. Failure would show that the proposed fragment type discards information required by a consumer. Pixel-perfect whole painting is not the exit claim.

### 3. Persistent inputs across a rendering episode

Use a font-resource change and a scroll-driven size effect in a small host history, with a CSSOM read between permitted rendering phases. Retain the old and new resource versions, effect sample, fragment output and presentation observation separately.

**Pass criteria:** derive which snapshot each query/sample may read; prove only the required update sequence, including deferral; reject stale-owner/font reuse and an extra resample that changes a forbidden intermediate observation. Do not assume output freshness or one global stable fixed point. This experiment fails if the temporal proof is only `TransitionMachine.run_iff` instantiated with an unexplained `Step` predicate.

## Practical plan and trust boundary

Prioritize experiment 1 over another generic architecture module or a large new property inventory. Give separate owners to the independent placement contract, the executable input builder, and adversarial integration review. Resolve the pilot's interpretation issues explicitly; do not let implementation convenience select a normative meaning. Then use experiments 2 and 3 as interface admission gates before broadening formatting families.

Keep the standalone spec/reference library independent of Gecko adapters. Existing source proofs can be imported with their exact domains; local native repair proofs must retain source versions and representation/provider obligations. No mathlib, external solver or source-translation capability claim is necessary for this milestone: select such tooling only after a concrete proof obligation requires it. Automation cannot decide the intended CSS relation or make an incomplete observer set complete.

Research blockers are faithful sufficiency/emergency interpretation, text/fragment ownership, approximation at branch boundaries and temporal composition. Many subsequent property constructors and case splits should become routine once those interfaces survive these tests, but that is a hypothesis to test, not a schedule. Whole-CSS completion ultimately requires closing every selected normative requirement and every transitive CSS-facing admission; kernel checking alone does not certify that inventory, prose interpretation, foreign providers or native translation.

### Evidence inspected

Prior `css-whole-spec-architecture-v5/REPORT.md`; current `css-spec-lean` README/ROADMAP/coverage map and the representative modules named above; fragmentation pilot SCOPE/REPORT and complete Placement/Selection modules. Primary draft sections linked above were retrieved during this assessment. `webspec-index` was unavailable, so primary web retrieval was used without installing tools. No new compiled sketch, build, browser execution, Git operation or native edit was performed.
