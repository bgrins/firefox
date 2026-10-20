# What would it take to cover all CSS in Lean?

Coverage and acceptance assessment, 19 October 2026. This is a proposal, not a new proof or an exhaustive normative inventory.

## Conclusion

A faithful, versioned formal account of all CSS is a plausible long-term research objective. A proof of one uniquely determined rendering for every document is not an appropriate objective: some behavior is deliberately left to implementations, devices or external specifications. Full coverage would mean representing those freedoms precisely, proving the obligations that constrain them, and accounting for every applicable requirement and dependency. It would not mean inventing an answer where the specification has none.

Our present work establishes useful semantic fragments. It does not yet establish that the source-to-requirement process scales to every CSS family. The next investment should be a complete versioned inventory and independently reviewed interpretations across several different kinds of specification, while implementation continues on useful slices.

## What changed since the previous assessment

The [previous coverage report](../../css-whole-spec-next-assessment-v1/coverage/REPORT.md) recommended a fragmentation requirement ledger. The [new pilot](../../css-fragmentation-requirements-pilot-v1/REPORT.md) implements it: 174 lexical units, 13 candidate obligations, four adjacent records, ten open providers and 18 complete linked theorem statements. Its validator reports 21 rejected corruptions and a relocated replay. **Independent interpretation review remains pending.** Those checks establish consistency of the supplied accounting, not completeness or correctness of its interpretation.

This assessment adds a concrete global inventory acceptance gate, broader family partition, rules for interpreting specification freedoms, and a progression from conditional models to a complete claim. It does not propose another accounting framework or repeat the existing fragmentation implementation task.

The local coverage records also need a single authoritative checkpoint. `ROADMAP.md` opens with the older origin extension, while `research/coverage-map.md` and `current-spec-inventory.md` describe the later ordinary-import/raw-scope checkpoint. This is documentation drift, not evidence of failed proofs. A whole-spec dashboard must bind accepted claim records instead of inferring current scope from prose summaries.

## 1. Define the complete target before measuring it

Maintain two explicit universe revisions: a dated stable baseline and a dated current-draft union. The current [CSS Snapshot](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/) supplies a baseline and clause replacement information. It is based on specification stability rather than browser popularity. It retains CSS2 margin collapsing when replacing other Box Model sections; selecting only the highest-numbered modules would lose requirements.

Reconcile the Snapshot with the [CSSWG draft catalog](https://drafts.csswg.org/) and [current-work index](https://www.w3.org/Style/CSS/current-work). The latter also points to Houdini and FXTF specifications. The current draft catalog includes emerging work such as Animation Triggers, Form Control Styling and Color HDR. Treat maturity, adoption and formal coverage as separate fields. No module disappears because Firefox does not implement it.

The proposed global inventory gate is:

1. Pin each acquired document, its status, source revision/hash, catalog memberships and conformance conventions. Catalog aliases and duplicate levels receive explicit identities.
2. Give every catalog entry a reviewed disposition: selected, replaced with residual clauses, historical theory, unresolved scope, or out of scope with a specific reason. A parked draft remains visible in the current-draft universe.
3. Reconcile every CSS2 chapter and appendix against explicit replacement edges. Record additions, overrides and surviving exceptions at clause level. A replacement title alone is insufficient.
4. Inventory properties, descriptors, at-rules, selectors/pseudo-elements, value functions, interfaces, algorithms and general conformance clauses. Compare these independent indexes against the document inventory; an orphan on either side blocks accounting completion.
5. Follow normative uses into external specifications and data. Record the exact imported contract and applicable clauses, not merely a bibliography entry. Repeat to a fixed point of identified dependencies, recording dependency cycles as joint obligations.
6. Have a second reviewer construct the roster independently from the catalogs and replacement statements. Reconcile discrepancies before freezing the universe revision. The current report has not performed that exhaustive enumeration.

External closure does not automatically mean formalizing every chapter of HTML or ECMAScript. It does mean identifying the obligations actually invoked by CSS and proving that an imported model supplies them. A supplied function without such a contract keeps the claim conditional. If an invoked contract entails a larger subsystem, that expansion is real work and must remain visible.

Roles and media are dimensions of this universe, not exclusions. CSS2 distinguishes rendering agents, readers/validators and authoring tools; the applicable duties differ. [CSS2 conformance](https://www.w3.org/TR/CSS2/conform.html#conformance) and [Speech conformance](https://drafts.csswg.org/css-speech-1/#conformance) also make device limitations and partial support relevant. A model should describe each applicable role and media policy without claiming one implementation performs every role. Unsupported syntax handling itself remains an obligation.

## 2. Family coverage and gaps

This matrix is grounded in `css-spec-lean/coverage.json`, its current coverage map and the new fragmentation pilot. “No integrated semantics identified” refers to those inspected artifacts; separate native bug capsules may prove local facts and require explicit import review. The matrix is a planning partition, not a finished module roster or requirement denominator.

| Family | Existing evidence | Work needed for family closure |
| --- | --- | --- |
| Syntax, recovery, nesting, namespaces | Scalar tokenizer, component consumers, recursive rule consumption, restricted source pipelines | Bytes/encoding; complete context dispatch and public parser entries; serialization; nesting; namespace environments; recovery across all registered features |
| Selectors, scope, pseudo-elements, shadow trees | Finite forest matching, logical/relational/structural selectors, specificity, bounded explicit/owner/import scopes | Complete validity and forgiving recovery; dynamic states; shadow/featureless/pseudo-element domains; host acquisition; all scope lifecycle cases |
| Cascade, inheritance, imports, custom properties | Bounded origins/layers/rollback/import histories; narrow variable pipelines | All properties and shorthands; presentation hints and encapsulation; full token substitution/registration; acquisition and mutation histories; cross-property invalidation |
| Values, units, calculations, environments | Exact numeric/type fragments, residual calculations, bounded opacity and visibility | Every value function and property grammar; rounding/ranges and irrational conversion; actual font/viewport/layout environments; all computed/used/resolved stages |
| Conditions, queries, containment | Supplied global truth and source-derived name-only container selection | Full media/supports/style/size/scroll conditions; unknown results; layout dependencies; containment; update and sampling order |
| Display, generated content, lists/counters | Generic style result; no integrated box construction identified | Anonymous/replaced/generated boxes; pseudo-elements; counter scope and formatting; box identities across DOM and style changes |
| Block/inline/float layout, sizing and positioning | Broad layout explicitly unsupported in the library | Intrinsic sizes; margins; line/float interaction; logical axes; containing blocks; relative/absolute/fixed/sticky and anchor positioning; cyclic dependencies |
| Flex, grid, tables, alignment, multicolumn | No integrated family semantics identified | Complete algorithms and exceptional cases; intrinsic contribution contracts; sublayout composition; fragmentation and overflow joins |
| Fragmentation, paged media, page-generated content | Conditional finite-grid model; implemented requirement map pending interpretation review | Actual break opportunities and geometry; sufficiency and emergency region; forced breaks; varying fragmentainers; pages, footnotes/running content and decorations |
| Fonts, text, writing modes, ruby, decoration | Font source inventory; separate local repair proofs, not integrated text layout | Font selection/loading and metrics; shaping, bidi, graphemes, line breaking, spacing, ruby and logical/physical mappings; resource histories |
| Images, color, backgrounds, borders | Opacity fragment; no integrated paint semantics identified | All image/color functions and resources; color spaces and numerical policy; background/border geometry; replacement content and output-device contracts |
| Stacking, transforms, effects, compositing | No integrated family semantics identified | Paint order and groups; 2D/3D transforms and flattening; clipping, masking, filters, blending, motion paths; observable output constraints |
| Animation, transitions, timelines, view transitions | Generic transition framework; separate conditional interpolation/provenance work | Concrete timing/effect/history semantics; all animatable value types; event order and replacement; scroll/view sampling; publication to style/layout/paint |
| Overflow, scrolling, snapping, UI and forms | No integrated family semantics identified | Scroll areas and positions; snap/anchor/overscroll; hit testing, interaction states, native controls and device policies; CSSOM observations |
| CSSOM, Typed OM, registration and Houdini APIs | Selected source/DOM observations; no full object model | Live objects, serialization, mutation and exceptions; callback/worklet contracts; object identity and host scheduling; integration with CSS computation |
| Speech and other media | Catalog inclusion; no corresponding library semantics identified | Speech values, sequencing and resource policies; non-screen observations; role/media applicability and device constraints |
| Cross-cutting host, security and compatibility | Bounded HTML/XML name and owner acquisition | HTML/DOM/flat-tree lifecycle; SVG geometry/style; Fetch/URL/CSP; privacy restrictions; quirks/legacy compatibility; Unicode and other normative data contracts |

The 127 historical feature records (120 checked fragments, seven unsupported) overlap and cannot be summed into a coverage ratio. Some old unsupported records coexist with later partial implementations. Likewise, a generic transition relation is not a formalization of CSS Transitions, and successful finite browser comparisons do not establish a universal engine refinement.

## 3. Account for clauses, then review their meaning

Reuse the source ledger and requirement pilot. Expand their unit of review to whole sections and adjacent dependencies, preserving tables, grammar, equations, links, normative advisements and document-specific conventions. Keyword search for “must” is insufficient: ordinary declarative prose and property-definition tables can impose obligations.

Each requirement needs stable identity, source revision, applicability, input domain, output observations, errors, choices, imported obligations and interpretation status. Keep stable parent obligations through splits/merges so changing granularity cannot manufacture progress. Generic rules require a complete instantiation registry: for example, a proved cascade algorithm does not discharge every property's grammar, inheritance, computation and animation behavior.

Use two independent readings before model acceptance:

1. A source reader derives obligations and adjacent context without seeing the proposed Lean definitions.
2. A model reviewer reconstructs the proposition, quantified domain and premises, and checks both missing obligations and accidental strengthening.
3. Reviewers reconcile omissions, conflicting readings and distinguishing examples. They retain dissent and unresolved questions rather than force consensus.
4. A separate proof/replay review checks the actual dependency closure, absence of hidden assumptions, admitted inputs and observations. Nonvacuity matters: prove inhabited permitted cases or exhibit a valid realization, not merely implications from impossible premises.
5. Mutation challenges remove a clause, narrow an admitted domain, swap a permission for a requirement, erase a provider premise and break a cross-family join. Some should fail mechanically; others must be caught by semantic review. Record which kind caught each fault.

Agents can propose inventories, interpretations, examples and proofs in parallel. Independent agent agreement is useful evidence, but correlated model errors remain possible. Difficult or contested readings need review by relevant specification/domain experts. Lean checks the formal proposition; it cannot certify that English prose was faithfully translated merely because the proof compiles.

## 4. Undefined behavior, choices and contradictions

| Specification situation | Required treatment |
| --- | --- |
| Deliberate UA choice | A constrained relation or policy parameter; prove the implementation's choice is allowed. Include the complete allowed set in semantic completeness claims, even if a reference implementation selects one member. |
| Device or external environment | An explicit environment with admissibility requirements and versioned contracts; do not silently treat arbitrary measurements as valid. |
| Underspecified detail | Preserve precisely the requirements that still constrain it; mark the unconstrained part. Do not use an “unknown” result as evidence that every actual behavior conforms. |
| Contradictory clauses | Record competing interpretations and an inconsistency witness where possible; keep the affected claim unresolved. Do not assume both inconsistent rules and prove results vacuously. |
| Evolving correction | Separate old and new requirement revisions; reopen affected claims. A discussion or resolution is evidence of interpretation, not automatically text in the selected specification revision. |
| Informative example or recommendation | Preserve its role and document conventions. Use it to challenge an interpretation without silently promoting it to a mandatory algorithm. |

These distinctions matter in real text. [CSS Text](https://drafts.csswg.org/css-text-3/#line-breaking) leaves aspects of line-break prioritization and hyphenation open while imposing other constraints. It also imports Unicode requirements and data. A faithful account must model both the open choices and the imported obligations; choosing one line breaker is not full semantic coverage.

The fragmentation pilot supplies a local contradiction example: visible class-B wording links to the class-A definition. The accounting correctly retains both. Neither a valid anchor nor a theorem about one reading decides the specification question.

## 5. Staged route and completion gates

| Stage | Concrete deliverable and gate |
| --- | --- |
| A. Freeze the universe | Independently reconciled module roster, CSS2 residual map, role/media matrix and external-contract frontier. No unclassified catalog entry. |
| B. Validate interpretation across different families | Finish independent fragmentation review; repeat clause accounting on font/text and HTML style-update contexts already acquired. Add one property-table-heavy family and one API/history family. Demonstrate that omissions and wrong permissions are detected. |
| C. Construct supplied inputs | Derive actual opportunities, geometry, value environments and host histories for useful domains. Every prior assumed provider has a named owner and explicit discharge target. |
| D. Close complete family slices | Cover all applicable requirements of a declared slice, including invalid input, all entry points and observers. Widen the master backlog rather than redefining “all CSS” around the slice. |
| E. Close interactions | Prove shared representations and observation contracts across style, layout, fragments, text, paint and temporal updates. Generated integration cases challenge the proofs; pairwise tests alone are not a completeness argument. |
| F. Publish versioned complete tiers | A reviewed normative account; separately a proved executable reference; separately engine refinement. A complete-tier claim requires every applicable requirement and transitive obligation at that tier, including allowed-choice fidelity and realization/progress where claimed. |

For Stage A, the useful next dispatch is an inventory producer plus an independent roster reviewer. For Stage B, assign domain readers before Lean implementers. Keep bug-driven work active: a local counterexample often exposes an integration obligation the inventory has missed. It must enter the ledger as evidence, not automatically as complete family coverage.

## 6. Largest uncertainties

- **Interpretation throughput and review quality:** the first complete semantic review of the new ledger is still pending; its cost cannot yet be extrapolated to CSS as a whole.
- **Composition:** abstract algorithms may be easy to prove while constructing their actual inputs and preserving observable histories is much harder.
- **External closure:** Unicode, text shaping, resources, host scheduling, numerical approximation and device output can dominate the effort. Provider assumptions cannot disappear into type signatures.
- **Specification gaps:** some questions need standards decisions. Formalization can identify the gap but cannot make a unique normative answer exist.
- **Evolution:** current drafts keep changing. Completion must name a frozen universe; ongoing maintenance is a separate continuing obligation.
- **Native refinement:** a complete semantic library would still leave the translation to Rust/C++, graphics, DOM, platform libraries and machine arithmetic to be established.

No completion percentage or calendar estimate is justified. First measure reviewed requirement-parent states, unresolved dependencies, interpretation disagreements, reopened assumptions and the effort to close real cross-family boundaries. Lines of Lean and theorem counts measure output volume, not whole-CSS coverage.

## Inspection limits

This assessment read the prior synthesis/coverage report, current library coverage JSON and map/inventory, roadmap, and new requirement-pilot report. It checked current official catalogs and representative conformance/text sources on 19 October 2026. It did not reread every artifact or CSS module, run Lean/browser tests, or independently reproduce the pilot's validation. `SOURCES.json` pins inspected local inputs and lists primary URLs. No native, build or Git changes were made.
