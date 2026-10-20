# Whole CSS in Lean: a concrete composition architecture

Research proposal, 19 October 2026. **No new CSS theorem, native refinement, browser result or compiled prototype is claimed.** Interface sketches below are uncompiled. V4 already supplies a checked generic read-episode protocol; this report supplies a proposed next architecture and acceptance boundary, rather than another generic protocol demo.

## 1. What “all CSS” would require

A whole-CSS project must account for every applicable requirement in a versioned normative universe: grammar and recovery, selectors, cascade and values, formatting and rendering, all selected media and conformance roles, APIs, temporal behavior, and normative HTML/SVG/Unicode/font dependencies. Superseded sections need residual-rule decisions. Newly published modules require explicit migrations. A version boundary makes the claim reproducible; choosing only convenient properties, screen media or finite static documents would narrow the objective and must remain a partial release.

Keep three different products:

1. **Normative model:** relations describing permitted outcomes and histories, supported by independent prose interpretation and requirement coverage.
2. **Executable reference:** algorithms proved sound for those relations, with declared-domain progress/totality and useful executable input adapters. A deterministic reference may choose one permitted policy; conformance does not require every browser to choose it.
3. **Gecko refinement:** particular native sources and representations simulate the model at declared observations, with compiler, runtime, providers and scheduling assumptions explicit.

The present project makes useful partial progress on each kind of evidence. It does not establish whole CSS. Kernel checking verifies the proposition supplied to Lean; it does not verify that the proposition means the specification, the complete observer set was selected, or a source binding is a semantics-preserving translation. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## 2. Start from the library that exists

The retained current files in `source/` support these migration decisions:

| Existing artifact | Reuse | Obligation before wider use |
|---|---|---|
| `CssSemantics/Style.lean`, `Style.compute_sound` | Selector/candidate/winner/defaulting composition pattern | Its generic value and forest contracts do not construct a complete browser style or layout tree |
| `Variables.lean`, `substitute_iff` | Independent substitution relation and executable correspondence | Enrich tokens with provenance, scoped ownership and dependency metadata; prove erasure to the old profile instead of silently replacing its meaning |
| `TransitionMachine.lean`, `run_iff`, `Runs.preserves` | Finite event-word execution and invariant transfer | Supply actual CSS steps; this does not establish fair scheduling or progress of an infinite host lifecycle |
| `CssFiniteScalar.lean` | Exact rational arithmetic with signed zero | Not a model of all CSS numbers, transcendental operations, machine rounding, overflow or layout thresholds |
| V4 `Protocol.lean` | Conditional equivalence when immutable providers agree on the requests actually made | Derive request owner, phase, epoch, provider consistency and finite plan construction from real callers |

The library's own coverage map explicitly leaves broad layout, font/text, painting, timing and browser refinement open. Separate repair capsules prove bounded statements about native-shaped operations; import only their exact theorem contracts, not their bug-fix labels or historical audit totals.

## 3. Repository and module split

Use one standalone repository initially, with independently buildable packages and one pinned dependency lock. Avoid dozens of separately versioned repositories before stable interfaces exist.

```text
profiles/                    reviewed requirements, editions, residual rules
packages/css-core/           identities, tokens, finite data, numbers, traces
packages/css-contracts/      versioned requests, observations, provider laws
packages/css-spec/           declarative CSS and host protocol relations
packages/css-reference/      executable algorithms + refinement proofs
packages/css-validation/     independent contracts, examples, mutation drivers
adapters/gecko/              optional source/version/representation bridges
releases/                   claim and transitive-assumption manifests
```

`css-spec` must not import Gecko or reference algorithms. `css-reference` imports the specification, not the reverse. Validation has separately authored observation expectations; shared parsers/classifiers are declared dependencies. A minimal Std-only core can remain portable; any analysis library needed for real/transcendental reasoning belongs in a pinned optional numeric package until required. Generated targets are disposable; releases retain source and receipts, not machine-local build directories.

Module ownership inside these packages:

- **Syntax/Selectors/Cascade/Values:** byte and Unicode admission, errors/recovery, selector trees, scope/priority/defaulting, typed value stages, registered properties and dependency graphs.
- **Structure:** DOM/flat/inheritance distinctions, pseudo-elements, generated and anonymous boxes, counters/lists, replaced content, source-to-rendered-occurrence identities. A node is not a box, and a box is not a fragment.
- **Formatting:** sizing plus block/inline/float/positioned/flex/grid/table algorithms, writing modes and containment. Text and fragmentation are cooperating clients, not postprocessing filters.
- **Text/Fonts:** font selection/loading/fallback, shaping contexts, character/cluster correspondence, whitespace, bidi, line opportunities, ruby and spacing.
- **Fragments/Geometry/Paint:** content continuation, decorations, coordinate spaces, transforms, stacking, scrolling/clipping, images, colors, filters/masks/blending, hit-testing and presentation.
- **Temporal/Host:** animation and transition states/events, query updates, resource availability, CSSOM reads/writes, HTML rendering opportunities, SVG instances, print and other profile consumers.

These families are a work partition, not proof that all requirements have been inventoried. Each profile requirement maps to one owner and all consuming interfaces; uncovered requirements remain open.

```text
Core → Contracts → Spec families → joint protocol/observation contracts
                     ↑                  ↑
                Reference + local refinement + progress
                     ↑
        native adapters + representation/source simulation
```

Imports are acyclic. Runtime feedback is represented in a joint protocol owned by a named integration module, never discharged by mutually assuming two providers are correct.

## 4. Concrete boundary design

### A. Rendering state and legal observations

Uncompiled Lean-like sketch; capitalized predicates are obligations to implement, not axioms to assume universally:

```lean
structure RenderState where
  trees : TreeState
  styles : StyleStore
  layout : LayoutState
  effects : EffectState
  resources : ResourceHistory
  phase : HostPhase
  choices : ChoiceHistory

inductive Action
  | mutate (edit : CssomOrDomEdit)
  | resource (delivery : ResourceDelivery)
  | renderOpportunity (stamp : TimeSample)
  | observe (request : ObservationRequest)

-- Outputs include public events, API replies and presentation observations.
def Step : Profile → RenderState → Action → List Observation → RenderState → Prop

def Simulates (rel : RenderState → NativeState → Prop) : Prop :=
  ∀ s n a out n', rel s n → NativeStep n a out n' →
    ∃ s', SpecSteps s a out s' ∧ rel s' n'
```

Internal work may stutter, but a proof must not erase an event or read by treating it as an internal transition. A separate progress theorem rules out endless internal stuttering before a required reply under declared host/provider conditions. `resource` does not permit arbitrary forged completion: delivery must satisfy ownership, request and policy relations. “Newest state” is not a universal observation rule.

### B. Layout/text continuation

```lean
structure FlowCursor where
  source : FlowIdentity
  position : ContentPosition
  nested : List ContinuationFrame
  context : FormattingContextIdentity

structure FragmentReply where
  fragments : List Fragment
  next : Option FlowCursor
  requests : List DependencyRequest
  progress : ProgressWitness

def FragmentStep : LayoutInput → FlowCursor → FragmentReply → Prop
```

`ProgressWitness` is family-specific: consumed content, a justified change of continuation phase, or a finite relaxation of a break constraint. It cannot be an unproved `Nat` supplied by the algorithm. Prove conservation of source content and explicit generated/repeated-content accounting, legal breaks, coordinate ownership, and decrease in a well-founded measure for a declared terminating domain. Sliced glyphs and repeated decorations are not duplicate source consumption.

For text, the request must include characters with source ranges, shaping context across relevant boundaries, font instance/features, writing mode/language/direction and epoch. The reply must relate clusters/glyphs/advances to that request. A `String → width` oracle hides CSS work and cannot support character hit-testing or fragmentation correctness.

### C. Contextual equality for retention

```lean
-- A family of downstream observers, not one serialized-value comparison.
def EquivalentFor (uses : List ConsumerContract) (x y : ValueState) : Prop :=
  ∀ c ∈ uses, ∀ h, c.AdmittedHistory h → c.Observe h x = c.Observe h y

def RetentionSound (same : ValueState → ValueState → Bool) : Prop :=
  ∀ old fresh, same old fresh = true → EquivalentFor admittedUses old fresh
```

A local comparator proof must include every admitted consumer and history. Attribute provenance, URL base data, scope ownership and dependency versions can matter when payload serialization is identical. The preceding animation investigations demonstrate why an unqualified global equality interface is inadequate. Expanding the consumer roster invalidates the retention contract; a generic `PartialEq` instance cannot silently discharge it. This is a proposed reusable proof boundary, not a claim that existing animation comparators meet it.

## 5. Stress-test the architecture with two dissimilar clients

### Text in variable-size fragmentainers

Scenario: inline text spans several styled elements, font availability changes, and the flow fragments across containers of different sizes. Shaping cannot simply be performed independently for each DOM node: CSS Text sometimes requires preservation across inline boundaries and sometimes requires breaks. [CSS Text §7.3](https://drafts.csswg.org/css-text-3/#boundary-shaping).

The layout contract must negotiate line content and shaping context while retaining source positions. Fragmentation also tracks progress under changing container geometry; a remaining pixel height alone is insufficient. The specification uses content and percentage progress in its varying-size rules, and defines fallback behavior to ensure progress when ordinary break restrictions cannot fit content. [CSS Fragmentation §§4.4–5.1](https://drafts.csswg.org/css-break-3/#unforced-breaks).

**Composition target:** if style-to-flow construction is faithful, shaping replies satisfy the reviewed font/text relation, each fragment step conserves accounted content and meets its progress contract, then the final fragments satisfy the selected layout relation and source-range observations. Font-change histories must reconstruct the affected inputs; equality of old and new total widths alone does not justify retaining glyphs. Initial implementation can restrict the domain, but restrictions stay visible and the remaining whole-CSS requirements stay queued.

### Scroll-driven animation that changes layout

Scenario: a scroll sample drives a size-changing effect; the resulting layout changes the scroll range. Solving for a geometric fixed point until nothing changes is the wrong generic interface. The current scroll-animation draft specifies sampling phases, an additional stale-timeline pass, and deferral of later changes; forced API layout reads do not invoke that additional procedure. [Scroll Animations §5.1](https://drafts.csswg.org/scroll-animations-1/#event-loop).

**Composition target:** the host protocol selects the permitted sample; the animation evaluator derives an effect; style/layout derive geometry; the subsequent phase retains or resamples exactly as the protocol permits. Prove the observable history, not merely a final rectangle. A persistent font/resource change belongs to a new admitted state transition. The V4 pure-provider theorem can optimize an individual immutable episode after these caller obligations are proved; it cannot decide which epoch CSS permits.

These clients share identities, histories and observers, but require different progress arguments. That is the main architectural test.

## 6. Difficult boundaries and who owns them

- **Termination:** flex length resolution has a concrete decreasing population of unfrozen items; prove that measure from its operations. This does not prove text layout, pagination or the browser lifecycle terminates. [Flexbox flexible-length resolution](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths). Pending external resources are legitimate waits. Infinite input histories need per-step progress and stated fairness, not a theorem that the entire browser halts. Fuel exhaustion remains `incomplete`, distinct from CSS invalidity.
- **Nondeterminism versus missing interpretation:** permitted UA choices need reviewed constraints and a realizable persistent policy. Underspecified or conflicting clauses remain unresolved. An arbitrary relation accepting all outputs is vacuous; a relation accepting none makes soundness useless. Require nonvacuity plus declared-domain availability and independently chosen observations.
- **Numbers:** retain exact symbolic quantities until the normative resolution stage. Specify implementation ranges and rounding separately. Small numeric errors can change line breaks or query branches, so uniform pixel epsilon is insufficient. At a discontinuity prove branch agreement or a permitted-outcome relation; do not invent tolerance. [CSS Values numeric types](https://drafts.csswg.org/css-values-4/#numeric-types).
- **Foreign inputs:** bytes of fonts/images, device facts and delivered events are honest inputs. Font selection, shaping boundaries, CSS URL eligibility, intrinsic size rules and effect publication are obligations owned by CSS/host modules. An unverified platform shaper or rasterizer may be an explicit conditional boundary, but then its CSS-facing behavior is not proved. Painting cannot be declared complete merely because a display list exists.
- **Native refinement:** caller admission, integer bounds, memory/lifetimes, generated bindings, cache effects and source-version transfer are separate from a Lean model. Complete Gecko CSS behavior spans layout, graphics and DOM code beyond Stylo. Finite paired browser evidence is valuable but does not discharge arbitrary native histories.

## 7. Prioritized milestones and gates

1. **Portable claim-preserving extraction.** Move the existing library into the proposed core/spec/reference split without changing meanings. Exit: fresh source-only replay, exact theorem/axiom/assumption rosters and an equivalence bridge for renamed interfaces. Keep browser tools optional.
2. **First complete vertical observation.** Use registered custom-property provenance through substitution and animation retention to one URL-eligibility observation. Existing counterexamples and local proofs make this tractable. Exit: actual constructor/caller histories, readiness, notification versus delivery, and an independent observer contract; neither a local taint theorem nor passing examples alone closes it.
3. **First real layout loop.** Implement the finite flex free-space loop with an independent relational allocation contract, progress proof and signed/exceptional numeric boundaries. Then integrate actual style-derived inputs. Exit: admitted input construction and a browser-independent executable reference, not only a normalized-input lemma.
4. **Hard composition pilot.** Implement the restricted text/fragment continuation and scroll protocol above. Exit: both cross-family histories preserve complete declared observations; deliberate wrong-owner, stale-epoch, dropped-content and over-eager-resample changes are rejected for semantic reasons.
5. **Expand by dependency closure.** Add formatting families, fonts/text, paint, host APIs and remaining media while assigning every requirement and provider. Exit per package: reviewed normative coverage, nonempty admitted domain, executable soundness/progress, dependency and observation closure, independent review; Gecko claims require an additional source/representation gate.

Parallel work units should be an independent spec contract, one proof implementation, and one adapter/observer investigation per interface. One integration owner resolves shared identity/phase changes; an independent reviewer challenges domain and observations. More proof-producing agents do not remove this integration bottleneck. No completion percentage or schedule is justified by current theorem counts.

**Recommendation:** keep the full target, release explicitly partial components, and spend the next implementation cycle closing one real cross-family observation rather than expanding unrelated theorem inventories. Whole CSS is a sustained language/graphics/host-semantics verification program; no Lean feature eliminates the interpretation, numeric, provider and composition research obligations.

## Evidence

`SOURCE-PINS.json` retains the exact V4 reports and current representative library modules inspected. `spec/FETCH.json` records fresh primary-source snapshots. All proposed interfaces and theorem shapes in this report are uncompiled. No native edits, Git operations, builds or browser runs occurred. The separate animation frontier remains checkpointed in `css-animation-equality-frontier-v1/CHECKPOINT.md` for later adjudication.
