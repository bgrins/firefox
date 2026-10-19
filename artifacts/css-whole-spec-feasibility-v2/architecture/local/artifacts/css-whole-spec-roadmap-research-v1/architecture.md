# Architecture for a comprehensive CSS semantics in Lean

Architecture research track, 19 October 2026. This is a design recommendation, not a new formal verification result. It complements [the requirement inventory](spec-inventory.md) and [the validation/evolution plan](validation-and-evolution.md); those tracks own the denominator, release accounting and review process.

## Recommendation

Grow the standalone library into a collection of **composable semantic packages with a small shared interface**, backed by a separate executable reference and implementation adapters. Preserve the existing reviewed fragments through explicit embedding/equivalence theorems. Do not first rewrite all existing modules, or create one giant interpreter whose successful compilation is treated as CSS correctness.

The final objective remains the entirety of the chosen CSS specification universe and its dependencies. Named profiles are intermediate milestones with honest boundaries, not a way to redefine that objective down to a small subset.

Keep three distinct deliverables:

1. **Specification model:** a reviewed account of every applicable requirement in a named, pinned CSS profile, including errors, permitted choices and interactions.
2. **Reference implementation:** executable decisions/algorithms that refine that model on their declared domain. A deterministic reference may select one permitted policy; it need not pretend every allowed rendering is identical.
3. **Engine refinement:** a relation connecting actual engine representations, providers, control flow, caches and observable histories to the model. Stylo adapters belong here, alongside separate Gecko layout, graphics, font and host adapters.

The baseline is [CSS Snapshot 2026, 22 June 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/). The selected Cascade 5, Display 3, Values 4, Sizing 3, Text 3, Conditional 5 and Web Animations 1 drafts are pinned by retrieved HTML hashes in `architecture-spec-pins.json`. They inform interface design; this research does not automatically add all their features to a supported release profile. Draft-versus-snapshot replacement decisions remain the inventory track's responsibility.

## What the actual repository suggests

Inspection found one Lake package and one `lean_lib CssSemantics`, pinned to Lean 4.35.0-rc4, with no extra Lake dependencies. There are 1,983 direct `CssSemantics/*.lean` files totaling 10,157,868 source bytes. These are organization measurements, not semantic coverage. I inspected representative modules rather than auditing all files; exact snapshots and the complete direct-module hash/import roster are retained.

| Inspected component | Existing useful pattern | Architectural limit to preserve |
|---|---|---|
| `Dom` / `Executable` | Abstract parent forest with a decreasing depth law; independent matching relation and executable iff theorem | This is an admitted element forest, not an automatically obtained DOM/flat tree or box tree |
| `SelectorModel` / `GenericStyle` / `Style` | Generic selector interface, candidate construction, cascade/defaulting composition | Model parameters and projections must remain explicit when stronger host/property profiles are attached |
| `Defaulting` | `PropertyProfile` carries inherited/initial information; executable and declarative resolution agree | A two-field property profile cannot own every property's grammar, stage dependencies, animation and CSSOM behavior |
| `Variables` | Independent reference/substitution relation with a supplied environment | The supplied map is an interface; computing it from registrations, inheritance and mutation history is another obligation |
| `CssFiniteScalar` | Exact rational arithmetic, signed-zero state, validity and correspondence lemmas | Finite rational semantics is a useful subdomain, not all CSS numerical behavior or an IEEE/Gecko proof |
| `CssTokenizer` | Input preprocessing, token relations, progress and executable equivalence | Scalar input is distinct from byte decoding and host resource acquisition |
| `CssScopeImportRun` / `CssScopeImportExpansionTotality` | Composed origin runs, source identity/provenance and explicit richness/admission premises | Resource/host premises must be discharged by providers; a stronger theorem cannot simply inherit them as facts |
| `TransitionMachine` | Generic finite state-transition fold, correspondence and invariant preservation | Despite the filename, this is not CSS Transitions or a Web Animations timing implementation |

Reuse these proof patterns. Add stable public facades and new packages incrementally; retain the old profiles as compatibility clients. The large flat module count suggests a need for semantic ownership and discovery, but does not by itself justify a mass refactor or imply proof duplication.

## 1. Shared semantic interface

### Identities, trees and provenance

Introduce distinct types for stylesheet instances, source occurrences, document nodes, styling subjects, boxes, fragments, resources and effect instances. Preserve source spans and the origin of generated objects. A pseudo-element subject must carry its owning subject and pseudo path. An anonymous box needs a generated-box role and provenance, rather than a fabricated DOM node.

Keep the DOM/element tree, flat tree, inheritance relations, formatting box tree and fragment tree separate. Provide reviewed conversions/relations between them. IDs for regenerated boxes/fragments can be snapshot-local; cross-update comparisons should use provenance and observable equivalence rather than assuming allocations retain identity. Display explicitly describes an intermediate box tree, generated and anonymous boxes, and subsequent fragmentation, making one universal `Node` representation a poor default. [Display introduction](https://drafts.csswg.org/css-display-3/#intro)

### Property registry and stages

Use a property-indexed interface whose specified, computed and used representations may differ. An ordinary longhand identity and a registered custom-property name are different identity constructors. For registered properties, the registration schema and its version belong in the typing context: changing registration can change the relevant value domain.

A property package should expose grammar/admission, initial value, inheritance, logical mapping, computation dependencies, used-value resolution, animation operations and serialization/observation contracts. Shorthands publish several longhands through a separate expansion contract. Shared metadata may generate identifiers and obligations, but it must not silently generate the supposedly independent reference and implementation from the same unchecked classifier.

The value-stage types are semantic boundaries, not a requirement to encode every intermediate record with elaborate dependent types. Start with small indexed interfaces and explicit witnesses where runtime registration makes the index dynamic. Cascade distinguishes declared, cascaded, specified, computed, used and actual values; it also permits fragment-specific value processing. Avoid treating a closed literal defaulting theorem as the entire computation stage. [Cascade value processing](https://drafts.csswg.org/css-cascade-5/#value-stages)

### Environments and dependencies

Replace an expanding bag of opaque numeric parameters with named, typed requests. Examples include `ParentComputed(subject, property)`, `FontMetric(fontKey, metric)`, `ContainerSize(container, axis)`, `ImageIntrinsic(resource)` and `TimelineSample(effect)`. A reply carries the producing environment version and a contract for that provider. The model must not accept an expected final style/layout result as the answer to a lower-level request.

Every computation exposes a sound dependency footprint. A footprint is allowed to overapproximate, but must include dependencies that influence validity, failure or fallback as well as the successful value. Cache validity follows from provider versions and delivered invalidation/recomputation, not a hypothesis that the cache already equals the expected output.

Different modules must refer to the **same** environment snapshot in a composition theorem. Independently existentially choosing a font or container size for each local lemma can make all lemmas true without describing any possible browser state.

## 2. Declarative relations, execution and partiality

For deterministic clauses, continue the existing pattern: an independently defined relation, an executable algorithm, and a proved iff theorem. For UA freedom, use a constrained relation over allowed outcomes plus an explicit policy that selects an outcome. Persistent policies should retain relevant choices across a history; unrestricted fresh choices at each step could hide inconsistent behavior.

Keep these outcomes separate:

- CSS-defined invalidity, ignored declaration, invalid-at-computed-value-time or recovery;
- a valid absent/unresolved value where the specification allows one;
- a request for environment data or a pending resource;
- unsupported behavior in this model/profile;
- an execution resource limit, which is not automatically a CSS semantic error.

An unresolved interpretation issue is neither arbitrary UA freedom nor an `Unsupported` implementation branch. Keep alternative relations/requirements visible until resolved.

For choice-bearing semantics, useful proof targets are `Exec(policy,input)=out → Spec(input,out)` and, where effective choice representation permits it, `Spec(input,out) → ∃ policy, Exec(policy,input)=out`. Do not demand a computable exhaustive enumerator for arbitrary real-valued results. Separate semantic completeness from executable completeness on a selected domain. The reference may instead return checkable certificates, symbolic values or bounded enclosures for operations that are not exactly decidable by a practical implementation.

## 3. Numeric architecture

Use several connected numeric layers:

1. Exact integers/rationals and signed-zero distinctions for syntax, ordering and appropriate arithmetic fragments.
2. An ideal semantic domain for dimensions, symbolic percentages, infinities/NaN where specified, and real-valued functions.
3. Explicit implementation policies for finite range, rounding, clamping, app units and device mapping.
4. Native representation theorems relating fixed-width/IEEE values and control decisions to those policies.

A single global epsilon is inadequate: discontinuities, comparisons, overflow, rounding stages and serialization have different obligations. Numeric approximation must preserve specified branch decisions where required; otherwise the observation relation must describe the actual permitted alternatives. Preserve unresolved percentages and indefinite sizes as typed states, not sentinel numbers. Avoid assuming advances/offsets are nonnegative without a local theorem.

CSS Values assumes ideal precision in the specification while permitting implementation-defined precision/range and conversion choices; it also specifies special numeric cases. This supports an explicit implementation-policy layer, not treating every discrepancy as permitted rounding. [Values numerical definitions](https://drafts.csswg.org/css-values-4/#numeric-types)

The existing `CssFiniteScalar` should embed into the appropriate finite subdomain with proved preservation. Add extended/analytic domains in separate modules and pin any analysis-library dependency rather than forcing all existing token/selector proofs to depend on it.

## 4. Layout, text and painting package contracts

| Package | Inputs and outputs | Essential integration obligation |
|---|---|---|
| Box construction | Styled subjects/text to boxes, generated roles, containing-block relationships and provenance | Explicit display/anonymous-box/pseudo rules; preserve content and style ownership |
| Geometry and writing modes | Logical axes, sizes, edges and transforms; conversion to physical coordinates | Inverse/composition laws, sign conventions and percentage-basis ownership |
| Intrinsic sizing | Typed query: axis, available space, definiteness, sizing phase and context | Distinguish intrinsic contribution from final used size; preserve specified cycle handling |
| Formatting contexts | Block/inline/floats, flex, grid and tables consume shared boxes/sizing interfaces | Each algorithm establishes its own placement, sizing, overflow and fragmentation obligations |
| Text/font services | Unicode/source mapping, whitespace, bidi, break opportunities, font matching, shaped clusters and metrics | Pin Unicode/font data; specify cluster/source coverage, ordering and valid metrics before using them in line layout |
| Fragmentation | Flow and available fragmentainers to ordered fragments and continuation state | Preserve content/decoration state and permitted break choices across boundaries |
| Painting | Fragments to stacking/paint order, transforms, clipping/filter groups and color operations | Define observable display-list/ideal compositing semantics before device rasterization refinement |

Do not make `layout : Box → Rect` the universal interface. Text can create many fragments, tables create multiple relevant boxes, and overflow/scroll geometry differs from the border box. Keep these observations distinct.

Sizing queries must name their phase because cyclic percentage rules change how contributions are computed; a generic least-fixed-point solver would need a proof that it implements the specified procedure. [Sizing intrinsic contributions](https://drafts.csswg.org/css-sizing-3/#intrinsic-contribution)

Text providers should be progressively discharged, not permanently arbitrary. Start with explicit Unicode/text transformations and controlled font metrics, then actual font selection/shaping contracts. Keep language-sensitive policy constrained: Text 3 leaves exact hyphenation choices open while controlling where hyphenation is permitted. This is a good pilot for separating a normative relation from a configurable reference policy. [Text hyphenation](https://drafts.csswg.org/css-text-3/#hyphenation)

Painting should first yield a semantic scene/display list that preserves order and grouping. Later layers can relate ideal colors/coverage to device pixels. Pixel equality must not be advertised while font selection, antialiasing or color conversion remains unconstrained. Speech/print can share values and generated-content interfaces while supplying different presentation backends; a desktop-only pilot must not silently define the whole project.

## 5. Animation and dynamic host composition

Model timing, effect-stack ordering, property animation operations and style publication separately. Property packages supply interpolation/add/accumulate contracts; animation packages supply order, underlying-value dependencies, resolved/unresolved timing and update histories. Then connect their result to the proper cascade origin. Web Animations explicitly folds effects over an underlying value and applies the result through the cascade, so animation cannot be a final pixel transform bolted onto static style. [Effect-stack composition](https://drafts.csswg.org/web-animations-1/#calculating-the-result-of-an-effect-stack)

The accepted conditional animation-identity component is an input to that work: it proves an identity/readiness/map invariant, not numeric interpolation, full effect order or the keyframe provider. Import it through a correspondence theorem; do not simply count it as full animation semantics.

Use a host transition relation for DOM edits, CSSOM changes, stylesheet/resource arrival, font availability, media changes, scrolling and timeline advancement. Internal update steps may be silent; public observations occur at specified checkpoints, including synchronous API flushes. Separate safety (a ready observation is correct), progress (a pending update can be delivered) and liveness (it eventually is under a scheduler/fairness premise).

The central incremental target should be: **after the required updates are delivered, observable incremental results agree with fresh semantics for the same document/environment history and permitted policy**. Do not assume every intermediate cache is fresh, or prove only a value equality while dropping invalidation dependencies. Preserve pending→skip→delivery counterexamples as tests of the scheduler interface.

Container queries and query units make the host/layout relationship explicit: some query values depend on the selected container's computed style and box dimensions. They require the specified selection and update protocol, not one unconstrained global condition Boolean. [Conditional Rules container features](https://drafts.csswg.org/css-conditional-5/#container-features)

Observation interfaces should include CSSOM specified/resolved values, geometry, paint output and relevant events. `getComputedStyle` must receive its own property-specific resolved-value projection; it is not definitionally equal to an internal `ComputedValue` record. Internal allocation IDs and irrelevant cache layout may be quotiented, but property identities, ordering and observable effects must survive that quotient.

## 6. Packages and agent integration

Keep one source repository initially, with separately importable packages or stable namespaces:

- `Core`: identities, provenance, collections, dimensioned geometry, numeric domains and outcome vocabulary.
- `HostContracts`: tree/resource/environment/timing interfaces and observation semantics.
- `Syntax`, `Selectors`, `CascadeValues`: reuse and adapt current modules through public facades.
- `BoxSizing`, `TextFonts`, `FlowLayout`, `FlexGridTable`, `Fragmentation`, `Paint`, `Animations`, `CssomHost`: independently owned semantic families.
- `Reference`: implementations selecting explicit policies, with correspondence proofs.
- `Profiles`: exact version/interface combinations and end-to-end composition theorems.
- `Adapters/Gecko`: source/representation/provider bridges outside neutral semantics.

These are proposed semantic boundaries, not a demand to create every package immediately. Keep the import graph acyclic by defining shared requests/relations low in the graph; model feedback as an explicit protocol/state machine above it. Avoid resolving real semantic cycles by pretending the corresponding dependencies do not exist.

Agent assignments should name a complete contract, its consumed/provided interfaces, interpretation questions, failure modes and a parent composition theorem. One owner reviews shared interface changes; sibling agents work behind frozen interface versions. Assign separate reviewers for normative interpretation and proof/source admission. A change to a shared value stage or environment contract must trigger dependent proofs rather than being hidden behind an unversioned oracle.

Required integration gates beyond isolated compilation:

1. Two actual clients use the shared interface, with conversion/correspondence proofs from their previous representations.
2. Producer guarantees discharge consumer premises with the same identity, environment version and observation projection.
3. A vertical theorem crosses the boundary, including invalid/pending/unsupported paths and a nonvacuous valid execution.
4. A counterexample or mutation demonstrates that omitting the key premise breaks the intended contract.
5. Public claims and replay evidence distinguish model, reference and native layers; no duplicate feature badge substitutes for composition.

The validation track supplies the detailed authenticity, spec-update and external-review procedure. This architecture adds the interface-level gates needed to make parallel work accumulate into one model.

## 7. Concrete next implementation pilots

### Pilot A — property stages and dependency publication

Start from the current closed style pipeline. Add a small property registry for `visibility`, `opacity` and one length/percentage property. The set deliberately exercises inheritance, numeric computation and used-value dependencies. Define invalidity/unsupported/pending outcomes and explicit dependency footprints. Embed the existing results without weakening them. Prove value correctness plus footprint soundness, then one parent-style/viewport mutation history whose delivered result equals fresh computation.

**Exit:** two existing consumers use the same registry; a stale-dependency mutant is rejected; specified/computed/used and CSSOM projections cannot be accidentally interchanged. This pilot closes interfaces before adding many more properties.

### Pilot B — box provenance and ordinary layout

Model an explicit ordinary block profile with text/replaced metrics supplied through typed contracts. Include `display:none`, `display:contents` and one anonymous-box case so DOM-to-box identity cannot be faked by a one-to-one mapping. Add logical axes, definite/indefinite sizing and a selected percentage dependency. Prove box/content provenance, geometry invariants and observable rectangle correspondence to an independent relation.

**Exit:** the geometry/box interfaces can express more than one box/fragment per subject; unsupported formatting contexts remain explicit; a separate layout client can consume the same intrinsic-size interface. This is a pilot, not an ordinary-block completeness claim until its requirement ledger closes.

### Pilot C — property identity plus actual animation values

Map the accepted conditional animation-identity component into the property registry through an explicit correspondence. Add one numeric interpolation family and the base/effect-stack dependency chain. Include registered-custom-property context as a separate provider obligation, because identity preservation alone does not establish that an endpoint was computed into the correct value representation.

**Exit:** computed keyframes → ordered effects → cascade contribution → observation is proved for the chosen profile, with a fresh/dynamic provider-change control. Keep full timing/events and other animation types explicitly outside this first profile.

Run A first as the shared-interface pilot. B and C can proceed in parallel once its minimal contracts are reviewed. Text/fonts and paint research can independently design their interfaces, but should not publish disconnected “full family” claims before a real client consumes them.

## Main blockers and decision

The hard work is resolving underspecified/overlapping requirements, choosing shared representations that preserve stage and provenance, closing text/sizing/environment dependencies, and proving temporal/native admission. Increasing the number of small theorems does not solve those interfaces. Numeric and UA latitude require relations precise enough to rule out errors while admitting legitimate implementations. Layout/text/paint introduce substantially different semantic objects from the current style pipeline.

A comprehensive versioned CSS model is plausible as a sustained research program. A complete correct executable reference is a further target with explicit numeric/policy/domain choices. Verification of all CSS behavior in Firefox is a still larger target spanning Stylo and other Gecko/platform components. The next useful commitment is the shared-interface pilot and its end-to-end theorem, with reviewed exit criteria rather than a completion percentage or speculative calendar date.

## Evidence and reproducibility

`architecture-local-receipt.json` records representative retained inputs; `architecture-module-roster.json` records the direct-module inventory. `architecture-spec-pins.json` binds complete retrieved HTML for the baseline and seven selected drafts. `architecture-web-*.json` retain primary-source browsing excerpts. Initial direct-network DNS failures are preserved; the authorized network retry retrieved all eight documents. The optional webspec-index helper remained unavailable after the parent's earlier bootstrap; primary web retrieval was used. No production-source mutation, Lean/browser/native build, test run or Git operation was performed in this research track.

The architecture checker verifies only this evidence's identity and internal inventory arithmetic. It does not certify the recommendations or reinterpret retained source as freshly accepted proofs.
