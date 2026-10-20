# A research program for whole CSS in Lean

Architecture assessment, 19 October 2026. This report proposes work; it adds no
proofs, native changes or browser results. Coverage accounting is a separate
workstream. External references were consulted during this assessment; their live
URLs are research references, not new pinned specification inputs.

## Recommendation

Pursue a standalone, versioned CSS semantics project, with a proved reference
implementation and optional engine adapters. Treat the first complete rendering
episode as the architectural experiment. Expanding property-by-property before
that experiment succeeds risks accumulating incompatible conditional models.

Whole CSS is plausible as a sustained research program. We have no evidence that
it is now a predictable implementation project with a reliable completion date.
Spec interpretation, interconnected layout, persistent host behavior and native
refinement are separate difficulties; generating Lean proofs addresses only part
of the work.

There are three different possible completion claims:

1. A normative relation faithfully covers the selected CSS corpus, including its
   permitted variability and host-facing requirements.
2. An executable reference produces permitted observations, and provides the
   required progress/availability, for every input in its declared domain.
3. A particular engine's implementation refines that relation across its actual
   representations, arithmetic, resources, invalidation and observations.

The third claim includes much more than Stylo. A stylesheet engine alone does not
implement text shaping, all layout, painting, DOM APIs or the browser's event
loop. The standalone project can reach useful releases without proving all of
Firefox, while retaining engine refinement as a separate objective.

## What I checked locally

These are observations of source definitions, not inferred capabilities from
module names. `INPUTS.json` records their hashes.

| Inspected component | Established architectural fact |
| --- | --- |
| `GenericStyle.lean` | Executable matching, candidate selection and defaulting connect to relations; computation consumes a supplied selector model/forest and property profile. This is a reusable composition pattern. |
| `CssFiniteScalar.lean` | Finite scalar values are exact rationals with signed-zero metadata; division returns an option at zero. This is not a representation of arbitrary real, infinite, NaN or transcendental CSS results. |
| `TransitionMachine.lean` | A finite token fold corresponds to a supplied step relation, given a per-step equivalence. It supplies neither the host step relation nor resource/event-loop progress. |
| Fragmentation `Placement.lean` | Inputs supply content extents, opportunities and decorations; selected cuts satisfy the grid predicate. Native layout does not construct these inputs by virtue of that theorem. |
| New fragmentation requirements pilot | Exact lexical accounting and 18 full theorem statements are linked, but interpretation review is pending and ten providers remain open. It creates no new Lean proofs. |
| `lakefile.lean`, manifest, toolchain | The current core has no third-party Lake packages and pins Lean `v4.35.0-rc4`. Introducing mathlib or a translator is a deliberate dependency change. |

The earlier assessment already recommended an input builder, two fragment
consumers and persistent histories. This report adds a package-level design,
specific numeric and text-provider decisions, proof acceptance contracts,
incremental-update obligations, tooling boundaries and migration experiments.

## Proposed packages and shared contracts

Start with one repository and separately buildable Lake libraries. Avoid a
separate repository for every CSS module: cross-module changes must be reviewable
and released together. The names below are proposals.

| Library | Owns | Must not silently assume |
| --- | --- | --- |
| `CssCore` | Source/token identity; typed property/value stages; tree and occurrence identities; dependency/resource versions; trace vocabulary | DOM node, pseudo-element, box and fragment identities are interchangeable |
| `CssSpec` | Reviewed normative relations, including permitted choices, exceptions and temporal requirements | An executable algorithm defines what CSS means |
| `CssReference` | Executable parser, style, flow, layout and observation policies | An unsupported input is invalid CSS; fuel exhaustion is a CSS result |
| `CssMath` | Real-valued/numeric semantics, geometry, transforms and color mathematics | Rationals cover transcendental results; a pixel epsilon preserves line breaks |
| `CssHost` | Explicit transitions for mutations, resource completion, animation sampling, API reads and presentation | Every observation sees a globally stable snapshot |
| `CssRefinement` | Component composition theorems and optional implementation adapters | A source hash, translation success or differential test is native refinement |
| `CssEvidence` | Source ledger, requirement bindings, challenge cases and claim/replay reports | Mechanical accounting decides prose meaning |

Use distinct types for source occurrences, subjects, generated boxes, text ranges,
fragments and resource versions. Define the maps between them, including
one-to-many and omitted outputs. Carry provenance through typed/untyped values,
computed/used stages and resource eligibility. A single generic `Value` record
with booleans for every stage makes invalid combinations too easy to express.

Define data structures by consumer needs, then prove each producer constructs
their invariants. For example, a fragment must retain source/box ownership,
continuation, writing mode, local geometry, transforms and paint inputs. Do not
store a final bounding rectangle and expect to recover text selection or ordered
fragment observations later.

An acyclic import graph does not imply one-pass CSS evaluation. Intrinsic sizing,
queries and effects require mutually constrained semantic components. Put each
cycle behind a joint relation and an explicit scheduling/progress contract; avoid
two components each assuming the other's correctness. Snapshot transitions can
then orchestrate these components without circular Lean imports.

### What a component must prove

Require four separately reviewed items, with exact theorem statements:

- **Soundness:** the actual selected output and observable trace satisfy the
  independent normative relation, under explicit input/provider assumptions.
- **Availability:** every admitted input has an output or a specifically permitted
  waiting transition. An empty relation cannot pass this gate.
- **Construction:** callers establish the assumptions rather than forwarding an
  unexplained `Corresponds` proposition. Each open assumption has an owner.
- **Preservation:** subsequent steps preserve identities, resource versions and
  invariants needed by consumers. A correct one-shot result is insufficient for
  mutation, animation or resource replacement.

A deterministic reference need not enumerate every permitted UA policy. However,
the normative relation must not lose allowed behavior simply because that policy
does not exercise it. Completeness of the model and soundness of its chosen
algorithm are distinct statements. Persistent choices need witnesses across a
history, not a fresh arbitrary choice at every read.

## The difficult foundations

### Numerics and layout

Keep exact rational arithmetic where it is faithful. Add a mathematical layer for
real-valued operations, with symbolic expressions where useful; preserve CSS's
special numeric values and stage-specific range rules explicitly. Prototype the
needed real/linear algebra in a separate mathlib-dependent library, rather than
reimplementing real analysis or forcing all parser proofs to import it. Mathlib
already provides a real-number foundation; that fact does not provide a CSS
rounding or approximation theorem. [Mathlib real-number module](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Real/Basic.html).

For implementation refinement, declare the supported representation, conversion
policy and operation semantics. CSS Values assumes abstract unbounded precision
in its descriptions while leaving supported numeric precision/range and some
conversion choices implementation-defined. The model therefore needs an explicit
implementation policy, constrained by the applicable clauses. [CSS Values
numeric types](https://drafts.csswg.org/css-values-4/#numeric-types).

A uniform final-coordinate tolerance is inadequate: one rounding decision can
change line count, fragmentation and all later positions. Prove branch stability
under a separation margin when available; at thresholds, prove the actual
rounded execution belongs to the permitted policy. Interval calculations can
help discover/prove safe branches, but an interval overlapping a threshold is an
unresolved decision, not permission to pick either outcome.

Layout families need their own measures: parser suffixes, finite track/box sets,
constraint stages and continuation progress. Do not infer global termination
from positive geometric progress. Separate finite rendering work from an
interactive document that can legitimately continue forever.

### Text, fonts and shaping

Define a shaping request with text/source ranges, script, language, direction,
font selection and features, boundary context and resource version. Its result
must retain clusters, glyph ownership and positioning, not just total width.
CSS prescribes conditions that require or prohibit breaking shaping across inline
boundaries, and includes qualified behavior elsewhere. That rules out an
unqualified per-element width oracle. [CSS Text boundary shaping](https://drafts.csswg.org/css-text-3/#boundary-shaping).

Separate three obligations: CSS font matching/fallback; text segmentation and
boundary behavior; a concrete font/shaping implementation. Start with pinned
fonts and a restricted checked shaper/domain to test composition, while exposing
the unproved provider. Then broaden script coverage and relevant external text
standards. External font bytes can be inputs; passing all CSS-facing selection
behavior to an opaque provider would leave CSS itself unverified. [CSS Fonts
matching algorithm](https://drafts.csswg.org/css-fonts-4/#font-matching-algorithm).

Do not promise verification of an existing general shaper without a separate
source, supported-language and numerical assessment. This assessment did not
establish such a translation route.

### Painting, compositing and APIs

Introduce a semantic scene containing stacking order, clips, transforms,
backgrounds/borders, glyphs, images, effects and color-space information. Prove
restricted paint composition before attempting an optimized GPU implementation.
Blending/compositing has explicit equations and grouping behavior suitable for
mathematical models. A proved scene is still short of proving rasterization,
decoding and hardware execution. [Compositing and blending](https://drafts.csswg.org/compositing-1/#generalformula).

Share fragment identities with CSSOM, hit testing and text selection, but give
each consumer its own observation relation. `getClientRects()` exposes ordered
fragments, including zero-sized ones, with transforms and special box handling;
bounding-box equality cannot establish it. [CSSOM View](https://drafts.csswg.org/cssom-view/#dom-element-getclientrects).

### Resources, time and incremental updates

Represent a history of inputs and transitions: DOM/stylesheet mutations, resource
completion/failure, viewport changes, animation sampling, style/layout flushes,
API calls and presentation. Retain resource and snapshot versions so a proof can
state which value a particular observation reads. Infinite resource waiting is
different from failure of a finite layout algorithm.

Specify update phases from their own sources. Scroll animation integration has
particular additional-update and deferral rules; a generic repeat-until-stable
loop is not an adequate replacement. [Scroll animation event-loop integration](https://drafts.csswg.org/scroll-animations-1/#event-loop).

After one-shot reference soundness, prove an incremental implementation preserves
observable equivalence to the appropriate fresh reference evaluation at the
required phase. This opens cache invalidation as a systematic verification area:
dependency tracking must cover every input read by the result. The reference
evaluation itself must use the correct historical snapshot, not today's final
state.

## Tools and trust decisions

| Tool | Proposed use | Limit |
| --- | --- | --- |
| Lean + Lake | Definitions, inductive relations, proof checking and build graph | The kernel cannot establish that our propositions faithfully encode prose |
| `simp`, induction, `omega`, `grind` | Routine structural, equality and arithmetic obligations | Does not invent the right interfaces or resolve CSS interpretation |
| mathlib | Selected real/geometry/color mathematics | Adds dependency/version maintenance; no automatic rendering model |
| Finite search, property generation, solver exploration | Find counterexamples, boundary cases and missing assumptions | Passing cases are not universal proofs |
| Charon/Aeneas | Experimentally translate suitable Rust components for refinement | Not a CSS-to-Lean translator, nor a current whole-Gecko pipeline |
| WPT/browser differential testing | Observable discriminators and implementation evidence | Shared browser behavior does not define the normative oracle |

`grind` produces Lean proofs using cooperating equality/arithmetic procedures;
its documentation explicitly describes limits for combinatorial search. Use
targeted automation with stable theorem interfaces. [Lean grind reference](https://lean-lang.org/doc/reference/latest/The--grind--tactic/).

Aeneas translates a supported safe-Rust subset through Charon and has a Lean
backend. Its current documentation lists unsafe/concurrent code as ongoing work
and identifies unsupported safe-language cases. External definitions can require
handwritten models. Pin translator, Charon, Rust and backend versions together;
first prove one representative component without silently replacing its hard
providers. [Aeneas documentation and limitations](https://github.com/AeneasVerif/aeneas#targeted-subset-and-current-limitations).

For release claims, inspect full statements and transitive axioms, replay from
sources, and use independent checker support where compatible. Keep native
evaluation assumptions explicit; current Lean documents per-computation axioms
and version-sensitive handling. A successful build alone does not certify the
meaning of a theorem or absence of assumptions in dependencies. [Lean proof
validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## Falsifiable milestones

These are integration gates, not estimates of completion percentage or dates.

| Gate | Deliverable | Failure that must prevent acceptance |
| --- | --- | --- |
| 1. Construct a real input | Source-derived styles and boxes feed the fragmentation pilot for a declared ordinary block domain; materialize the actual chosen cut | Caller still supplies opportunities/sufficiency, or a zero-size/preceding-deferral case breaks source accounting |
| 2. Preserve text ownership | Supported font/text requests produce glyph clusters, lines and fragments across an inline boundary | Width agrees but glyph/source ownership or required shaping continuity differs |
| 3. Two consumers | One fragment result supplies ordered CSSOM rectangles and a restricted paint scene | Dropping a zero fragment or substituting a glyph goes undetected by the combined contract |
| 4. Numeric discontinuity | Exact and implementation-policy versions of one sizing/line-break algorithm are related, including a threshold case | Proof uses only final epsilon, or excludes every interesting boundary through an unjustified premise |
| 5. Dynamic episode | Font arrival or a style mutation, an effect sample and an intervening API read produce a permitted versioned trace | A stale cache and a fresh computation are indistinguishable to the proposed observer, or an extra resample is silently allowed |
| 6. Native component | Translate or explicitly model one actual source component and discharge its representation/providers against a shared normative relation | Source hashing, extracted control flow or finite tests are the only native correspondence |
| 7. Evolution and portability | Replay a standalone release, then migrate a genuine spec correction and an interface change without Gecko/network dependence in the core | Old claims silently change meaning, a downstream obligation is omitted, or the core requires local Firefox artifacts |

Each gate needs nonempty admitted examples, near-boundary rejection examples,
independent interpretation and a deliberate semantic fault that the claimed
observation/proof rejects. Gates 2–5 can expose an interface failure requiring
redesign; that is valuable research evidence.

Only after these pass should broad parallel family work accelerate: sizing and
writing modes; flex/grid/table/positioned/fragmented layout; text/fonts; paint and
effects; CSSOM and host histories. Preserve unresolved domains in the whole-CSS
backlog. A small vertical release is an experiment, not a redefinition of all CSS.

## Agent workflow and sustainable releases

Use a three-role work unit: one interpreter derives the contract and adversarial
examples from source; one producer implements relations/reference/proofs; one
reviewer checks interpretation, assumptions, nonvacuity and composition. Native
adaptation is an additional lane when needed. The interpreter should record its
oracle before seeing the producer's choices. Agents can generate code, proofs,
counterexamples and dependency proposals; review must still resolve meaning and
scope. One maintainer owns shared interfaces and jointly reviews cyclic changes.

Limit production to review capacity. Prefer one accepted provider closure over
many new assumed-provider modules. Track effort and queue time separately for
interpretation, proof, provider closure, review and migration; track reopened
requirements and downstream change fan-out. Those measurements can support a
later staffing estimate. Current theorem counts cannot.

Keep source locks and stable semantic requirement IDs separate. A spec watcher
should propose a change review; it must not silently rebind a theorem to edited
prose. Store whether a migration proves equivalence, one-way inclusion or a
genuine behavior change. The existing cloned-decoration correction is a useful
first exercise, but add a shared-interface migration that actually changes a
consumer type to test composition maintenance.

Pin each release's Lean/dependency/source versions. Use one supported toolchain
per release; evaluate upgrades on a migration branch with full replay. Mathlib
toolchain/dependency updates are coordinated and require rebuilding clients.
[Lean project maintenance guidance](https://leanprover-community.github.io/install/project.html#updating-mathlib-in-your-project).
Partition CI by import dependencies for routine work, with full source replay
for releases; cache keyed by exact inputs, and delete only reproducible obsolete
build outputs. Do not duplicate complete tools and dependencies in every proof
artifact. Preserve concise replay receipts and source identities centrally.

The standalone repository should expose a library API and a small reference CLI,
with optional Gecko adapters consuming a pinned release. Vendoring that release
for verification is reasonable; a runtime Lean dependency is not required.
Publishing alongside the CSS specifications can mean linked requirement cards,
machine-readable change reports and formal clarification proposals. It must not
suggest that CSSWG has endorsed a model unless that actually happens.

## Possible hard stopping points

Literal completeness may be blocked by unresolved normative ambiguities,
inconsistent cross-spec rules, qualified requirements without an agreed formal
interpretation, or insufficiently specified host behavior. Preserve alternatives
and request clarification; neither an arbitrary relation nor an invented
deterministic rule solves those cases.

Other obstacles are engineering/research obligations rather than fundamental
impossibility: composition proof size, numerical branch behavior, text-provider
verification, native unsafe/concurrent boundaries and keeping pace with changes.
There is no reason to expect a general automatic decision procedure for all of
these. A mature project would maintain reviewed partial releases and explicit
open obligations while pursuing the full versioned target.

The decisive next question is whether the current independently proved pieces
can construct and preserve one faithful rendering episode. That result would
justify a much larger parallel program more strongly than another increase in
isolated property or theorem counts.
