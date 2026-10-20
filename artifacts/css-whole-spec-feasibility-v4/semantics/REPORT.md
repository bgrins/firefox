# Whole CSS in Lean: make cross-family dependencies executable

Research proposal, 19 October 2026 UTC. This extends v3 with a **compiled read-episode interface and composition theorem**, exercised by sizing and animation clients. It does not implement CSS sizing or animation algorithms. All other interfaces below are proposals. The endpoint-taint proof is unchanged and outside this workstream.

## 1. Decision and concrete result

Use two semantic layers: **immutable dependency-reading episodes**, connected by an explicit **state-changing host/rendering protocol**. Do not force the whole browser into one pure evaluator or let mutable providers answer a pure episode inconsistently. A CSS request must identify its semantic subject, producer/owner, phase and permitted history version before execution. These fields are not evidence that the chosen request is correct; deriving them is a separate caller theorem.

The prototype in `prototype/Protocol.lean` has dependent requests: size replies are `Basis`, timeline replies are `Option Nat`. A `Plan` can branch on a reply, so its future dependency list is not known statically. Its evaluator returns both a value and the ordered requests actually made.

```lean
abbrev Provider := {α : Type} → Request α → α
inductive Plan (α : Type) : Type 1 where
  | done : α → Plan α
  | ask {β : Type} : Request β → (β → Plan α) → Plan α

-- Compiled theorem; AgreesOn compares replies to every actual request.
theorem actual_footprint_sufficient (plan : Plan α) (left right : Provider)
    (agree : AgreesOn left right (run left plan).2) :
    run left plan = run right plan
```

This is stronger than equality of returned values: replacing a provider cannot change the branch taken, omit a failed lookup, or introduce a later request. `run_bind` proves sequential clients concatenate their actual traces. The theorem is about this evaluator, **not an independent declarative CSS reference**. A browser cache is not implemented: checking agreement by recomputing all old requests may cost as much as evaluating the client. Efficient version certificates need their own implication to `AgreesOn`.

### Two dissimilar clients, one composed episode

`sizingClient` selects initial-treatment versus a definite-basis calculation. `animationClient` reads a prescribed timeline epoch, then reads a used-size basis only when the sample is active. `demo` sequences both. Exact compiled observations:

| Provider | Contribution | Effect | Requests |
|---|---:|---|---|
| Fixture | 20 | progress 25, displacement 25 | intrinsic size at epoch 8; sample at epoch 5; used size at epoch 8 |
| Erase sizing phase | 20 | progress 25, displacement 0 | Same request list, wrong answer to used request |
| Force latest sample | 20 | progress 75, displacement 75 | Same request list, wrong answer to sampled request |
| Inactive sample | 20 | inactive | Intrinsic size and sample; no used-size request |

`none` remains in the dependency trace; an inactive-to-active change is observable. Another theorem rules out replies 25 then 75 to the **same key in the same pure episode**. A stateful producer with that behavior cannot be admitted by asserting local answer validity; it needs distinct contexts or a transition between episodes.

The numbers, natural-number arithmetic, keys and sampling policy are constructed fixtures. The fixture's `.initial → 20` is an assumed intrinsic contribution, not a derivation of CSS `auto`. The mixed epochs illustrate an interface capability, **not proof that CSS permits this particular pair**. Phase and epoch erasure are discriminating model examples, not browser bug reports. Thirteen checked results comprise two generic composition theorems, three client corollaries and eight boundary/witness results; theorem count is not spec coverage.

## 2. Normative pressure on this interface

Three short source checks justify the distinctions; no full normative trace is claimed for the fixture:

1. Cyclic percentages use special intrinsic-contribution rules and different used-size handling, with axis/formatting exceptions. **REACHED:** phase must affect the request; a numeric percentage-basis function alone cannot choose the applicable rule. [Sizing 3 §5.2.1](https://drafts.csswg.org/css-sizing-3/#cyclic-percentage-contribution)
2. Scroll timelines have a defined rendering-update sampling protocol. A final layout change can await the next rendering update; forced style/layout APIs do not perform the extra initially-stale procedure. **REACHED:** newest layout is not a universally correct replacement for a prescribed sample. [Scroll Animations §5.1](https://drafts.csswg.org/scroll-animations-1/#event-loop)
3. CSSOM resolves different properties to computed or used values, with conditions including box-generating display. **REACHED:** an observation is not simply serialization of whichever style value is already cached. [CSSOM resolved values](https://drafts.csswg.org/cssom/#resolved-values)

The key-production theorem remains **INCONCLUSIVE/unimplemented**: there is no selected CSS caller or engine adapter in this prototype. Axis, writing mode, replaced status, property, formatting context, numeric policy and resource/choice histories must be explicit or proven captured by a context identity in a real interface revision. Current natural-number identities carry none of those invariants.

## 3. Implementable module boundaries for the full target

Use a standalone library with `Contracts`, `Spec`, `Exec`, and `Refinement` namespaces. Only `Refinement.Gecko` imports engine representations. This is the proposed ownership partition, not an assertion that the list itself inventories all CSS clauses:

| Module family | Owns | Produces / must prove |
|---|---|---|
| Core + Profile | Versioned identities, source spans, ordered data, numeric domains, observation vocabulary, normative editions | Namespace-safe IDs, source/profile consistency; no unowned active requirement |
| Syntax + Selectors + Cascade | Recovery, matching against appropriate trees, scope/origin/layer ordering, declarations, custom-property dependencies | Parsed programs and specified/computed values with provenance and metadata; raw-input admission |
| Values + Properties | Per-property stages, units, percentages, interpolation, registration/defaulting, serialization | Dimensioned expressions and dependency requests; do not resolve unavailable layout bases early |
| Structure | Display, anonymous/generated content, pseudo/flat/inheritance trees, counters/lists, structural transform/containment effects | Box identities and source ownership; generated/suppressed/repeated-content accounting |
| Layout | Block/inline/float/positioned, flex/grid/table, replaced and intrinsic sizing | Formatting-specific relations, request construction, geometry and overflow; phase-specific cycle rules |
| Text + Fonts | Matching/fallback/loading, bidi/whitespace, shaping boundaries, spacing, ruby, writing modes | Source/cluster correspondence and negotiated line content; loading and reshaping dependencies |
| Fragmentation | Lines/pages/columns, break legality, continuation and repeated decorations | Progress and content conservation across different fragmentainer constraints |
| Geometry + Paint | Transforms, stacking, backgrounds/borders, images, color, masks/filters, blending, scrolling/clip effects | Scene relation, coordinate conversions, geometry and hit-test observations; scoped rasterization relation |
| Temporal | Transitions/animations, timelines, queries, resource/scroll changes | Episode selection, event/transition creation, invalidation and observation histories |
| Host + APIs | CSSOM mutations/reads, HTML rendering/lifecycle, DOM/shadow, SVG integration, UI/print/speech consumers | Typed events, tree adapters and host obligations; observable serialization, geometry, events and presentation |

SVG cannot be reduced to one box per DOM element: its rendering structure excludes some elements and repeats others with context-dependent styling. Keep source identities separate from rendered occurrences. [SVG 2 rendering tree](https://www.w3.org/TR/SVG2/render.html#RenderingTree)

The import DAG is acyclic even where runtime protocols interact:

```text
Core/Profile → Contracts → Spec.{Style,Structure,Layout,Text,Paint,Temporal,Host}
                       ↘ Exec implementations → per-family soundness/progress
Spec relations + local proofs → protocol composition → observation theorem
Native source + adapters + representations → Gecko simulation → same observers
```

`Contracts` defines request types; it does not assume all replies correct. Recursive layout/text or query/layout interaction must be represented by an owned joint transition relation, not circular assumptions between separately verified providers.

## 4. Two further interfaces needed before expansion

The following are **uncompiled sketches**, intentionally not added as axioms:

```lean
structure EpisodeAdmission (w : World) (o : ObservationRequest) where
  context : ReadContext
  provider : Provider
  selected : ProtocolSelects w o context
  keys : RequestsWellFormed context
  replies : ProducerRelations w context provider
  choices : JointChoiceHistoryValid w context

inductive HostStep : World → HostEvent → List Observation → World → Prop

-- The executable episode is related to independently defined CSS clauses.
theorem episode_sound (a : EpisodeAdmission w observation) :
  BuildPlan a.context w observation = some p →
  SpecObserve w observation (run a.provider p).1 (run a.provider p).2

-- A browser may stutter internally, but not lose a public event.
theorem engine_step_simulates :
  Related spec impl → EngineStep impl event trace impl' →
  ∃ spec', HostSteps spec event trace spec' ∧ Related spec' impl'
```

Every field creates an owned obligation; filling `ProducerRelations` with `True` or with the desired final result would not implement CSS. Request traces are internal dependencies, not public events. The prototype has no event emission or resource requests; the second theorem must relate full event traces, not apply `actual_footprint_sufficient` to hide side effects. HTML's rendering task sequence is itself part of the joint contract. [HTML updating rendering](https://html.spec.whatwg.org/multipage/webappapis.html#update-the-rendering)

For layout/text, use a separate request with content slices, candidate breaks and shaping context, and a reply relation that accounts for source content and permitted shaping. A fragment step returns committed fragments plus a continuation. Glyph equality is too strong; arbitrary glyph/width answers are too weak. V3 retains the primary Text/Fragmentation source analysis; this task has not implemented that relation.

## 5. Obstacles that require research, not more leaf lemmas

- **Cycles and termination.** `Plan` is inductive: a run with total replies has a finite request path. This is not a machine time/space bound or a claim that every mathematical provider is executable. Constructing a finite plan from arbitrary admitted CSS/layout input is unproved. It cannot represent indefinitely pending resources or unrestricted feedback. Use separate small-step state relations for these, then prove local progress under appropriate conditions. Percentage cycle rules, fragment relaxation and sampling order need different measures/contracts. Fuel exhaustion must be reported as incomplete execution, never converted to an allowed CSS result without a normative rule.
- **Persistent permitted choices.** A pure provider represents one chosen world, not all UA latitude. Per-query nonempty answer sets can be jointly inconsistent. Specify permitted policies/history consistency and prove joint realizability; an implementation may refine an allowed policy. Distinguish normative choices from missing interpretation. The repeated-key theorem exhibits one required coherence condition but does not prove the whole policy system consistent.
- **Numeric branches.** Exact rational/extended expressions belong in the relational layer; implementations need context-specific range/rounding contracts, including threshold outcomes. The specification assumes ideal precision while allowing implementation-defined supported precision/range and constrained conversion. A universal epsilon bound would hide changed line breaks or query outcomes. Transcendentals, singular transforms, exceptional values and serialization require dedicated theories/adapters. [CSS Values numeric types](https://drafts.csswg.org/css-values-4/#numeric-types)
- **Time and hidden reads.** Pure provider admission requires immutable/versioned replies during an episode, or proof that mutations are unobservable there. Host reentry or callbacks break this model unless a new episode is created. No theorem here derives compatible epochs, cache invalidation, or a shared key from native getters. Failed queries, resource availability, policy versions and metadata can matter even when values serialize identically.
- **Foreign providers.** Font bytes, device/input facts and delivered events are legitimate external inputs. Correct CSS font selection, shaping boundaries, computed style, layout dimensions, URL eligibility and query selection are CSS work still owed. A platform shaper/rasterizer can initially be a documented unproved contract; doing so makes the result conditional, not full coverage. Host standards may be separate verified components; their CSS integration cannot vanish into an unconstrained oracle.

## 6. Migration and next acceptance gates

Current inspected library modules are reusable: `CssNumericEnvironment` proves percentage arithmetic against a supplied dimensioned basis; `Style` composes supplied forests/profiles and cascade; `TransitionMachine` proves finite state/token runs. Adapt these into the shared contracts while preserving their assumptions. None currently derives the prototype's request keys. Keep generic proofs distinct from versioned CSS interpretations; do not replace established modules wholesale.

Prioritized work units and gates:

1. **Close the prototype's actual CSS adapter.** Select one full non-replaced sizing scenario, derive intrinsic/used keys and independent clause results, and connect the existing numeric resolver. Require a second real consumer and phase/owner counterexamples. This is the highest-value implementation pilot.
2. **Add a real observation protocol.** Derive the sample plan from a finite host history; include inactive/active and query-triggered transitions. Prove admissibility and nonempty executions independently of the interpreter. Reject both arbitrary stale answers and unconditional latest answers.
3. **Exercise a structurally different boundary.** Implement one text/line/fragment continuation with content conservation, legal break choices and local progress. Include re-shaping and changed available width; pixel equality is not the reference oracle.
4. **Expand families in parallel against stable interfaces.** Assign requirements, clause interpreter, executable algorithm and independent review separately. Changes to request/observer contracts invalidate downstream bindings. Integrate with two dissimilar consumers before calling an interface stable.
5. **Close engine paths independently.** Bind complete native loops, actual constructors, metadata/caches, machine arithmetic and scheduling to the model. Finite extracted/native/browser agreement challenges the bridge but does not prove it. Keep all remaining premises transitively visible.

Inventory IDs are in `INTERFACES.json`; all are `proposed`, with separate model/executable/native status. They may be mapped to the inventory agent's schema, but no normative requirement should become accepted merely by referencing this prototype.

## 7. Meaning of entirety and evidence

“Entire CSS” must mean every applicable requirement and interaction in a reviewed, versioned normative universe, including host dependencies and print/UI/SVG/text/font/temporal behaviors—not only the properties currently supported by one engine. Future standards require another revision; ambiguity remains an explicit unresolved obligation. Modeling all requirements, proving an executable reference, and proving Gecko refinement are separate release claims. There is no supported completion percentage or timetable.

Kernel checking establishes the written theorems under their axioms. It does not establish inventory completeness, correct prose translation, faithful caller keys, browser execution, external provider contracts, or hardware/compiler correctness. Here the only proof result is the finite read-episode composition component and its synthetic clients. Axioms are `propext` or none; no `sorry`, custom axioms or `native_decide` are used. Primary pages and anchors are retained in `spec/`; the unavailable webspec-index was replaced by direct primary retrieval. No native changes, Git operations, Firefox build or browser run occurred.
