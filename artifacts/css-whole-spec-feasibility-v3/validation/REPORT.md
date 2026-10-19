# Whole-CSS validation: challenging a completion claim

19 October 2026. Research proposal, extending the first roadmap and v2 validation report. No new Lean theorem, engine acceptance, browser execution or implementation change is claimed. The retained local receipts below are historical evidence used to design the program.

## 1. Decision and scope

A standalone CSS semantics library is a plausible research program. A claim that it covers all CSS needs an explicit, finite release profile and a much stronger argument than a collection of proved algorithms. Start from the dated CSS Snapshot 2026 inventory; record selected draft revisions, supersession rules and external standards separately. The Snapshot distinguishes stability from implementation uptake and cautions about editor drafts. A moving “latest CSS” claim cannot be frozen or reproduced. [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/)

The useful next investment is an adversarial acceptance process applied to representative vertical slices. This report proposes that process. It adds to v2: independent challenge contracts, explicit quantifiers for permitted variability, cross-family observational composition, a metadata-preservation trace, and a concrete semantic-change exercise. It does not repeat the earlier prior-art survey or treat the historical library's feature-record count as a coverage denominator.

Three distinct deliverables should remain visible:

1. **Interpretation:** a reviewed mathematical meaning for a pinned normative requirement, including alternatives and unresolved questions.
2. **Reference:** executable behavior proved to implement that meaning over a stated input/environment domain.
3. **Engine:** a refinement from actual source, providers, callers and temporal state to the reference relation, with explicit native assumptions.

The current work has useful components and discovered bugs. General layout, fragmentation, shaping, painting, interaction, full parsing/cascade composition and browser scheduling are not collectively verified. Refuted global partition/locality targets remain refuted; new repairs do not retroactively prove their original baselines.

## 2. What would falsify “complete”?

For each requirement, a reviewer should try to construct one of these counterexamples before approving its completion state:

| Challenge | Evidence required to reject it |
|---|---|
| A normative exception was omitted or the wrong spec level won | Reviewed requirement text, replacement graph and branch examples |
| The model proves a weaker statement than the approved contract | Independently owned challenge statement, expanded definitions and explicit domain |
| A required browser input is excluded by a convenient premise | Caller admission from the public entry point, or a visible unresolved obligation |
| A supplied provider already assumes the desired conclusion | Independent provider contract, implementation bridge and nonvacuity witnesses |
| Value equality hides taint, origin, ownership or cache state | Contextual observation contract covering every downstream consumer of that metadata |
| Independently valid calls cannot occur in one valid history | Shared environment/state relation maintained over the whole operation sequence |
| Different subsystems each satisfy local rules but disagree on a boundary | A composition theorem or a named open join, with a discriminating integration test |
| Tests pass because the feature or assertion did not run | Exact test identities, prerequisites, assertion paths, harness completion and source/binary binding |
| Proofs survive after the wrong source body is extracted | Independent extraction checks, complete body/provider pins and source mutation controls |

Store a dependency graph from requirement to interpretation, definitions, theorem contracts, reference code, native adapters, observations and assumptions. A release claim inherits every unresolved premise reachable from its root. A shared open premise is a cut through all dependent claims; it must not disappear when a component is copied into another package. A proposed claim linter can detect missing edges and stale hashes, but cannot decide whether an interpretation or assumption is justified.

“Complete abstract semantics for profile P” requires every in-scope normative obligation and interaction to have a disposition, and no unresolved semantic choice disguised as a theorem parameter. “Complete executable reference for P” additionally requires termination/productivity and sound correspondence over that domain. “Engine E refines P” additionally requires entry/readiness, representation, source and provider joins. A finite test suite is supporting evidence at all three levels, never a replacement for their universal obligations. A conditional result is valuable, but must name the condition in its release claim.

## 3. Preventing a large incorrect model

### Independent interpretation before proof production

Have one worker derive scenarios and expected observations from the normative call chain without seeing the proposed algorithm. Have another propose definitions and theorem contracts. A reviewer reconciles disagreements against primary text, surrounding exceptions, resolutions and existing tests. Preserve rejected interpretations and a minimal distinguishing example. Escalate genuine ambiguity as a documented CSSWG question; do not choose the interpretation that makes the current code easiest to prove.

Freeze the challenge contract separately from producer proofs. Inspect its referenced definitions, notation, typeclass instances, empty-domain cases and hypotheses. Require concrete admitted examples and examples that reject a tempting incorrect interpretation. A theorem about a token list supplied by an oracle does not close tokenization; an invariant conditional on fresh style does not establish invalidation.

Lean's validation guidance distinguishes validity of a proof from meaning of its statement. Exact axiom inventories and fresh kernel rechecking improve assurance. Independently stored challenge statements and comparator/external-checker workflows offer an additional contract check, while still trusting the challenge's meaning and checker infrastructure. Adopt these selectively for release roots and shared foundations; pin the actual supported tool versions. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

### Variability needs the right quantifiers

Represent permitted behavior as a relation over a persistent environment and history, not as an arbitrary answer supplied independently at each call. A fixed engine strategy may be conforming without implementing every allowed strategy. Conversely, a semantics advertised as the whole permitted behavior must not silently select one strategy and exclude the others.

For example, a soundness claim can have the schematic shape `for every admitted history h and engine observation o, Engine(h,o) implies Allowed(h,o)`. Its environment choices must satisfy the standard's stability and dependency constraints throughout h. Do not replace that with “for every output, there exists an unconstrained provider that explains it.” For an executable chosen strategy, prove membership in Allowed; claim completeness of the relation only with a separate argument.

CSS Text provides useful adversarial cases: `line-break:auto` deliberately leaves selection of restrictions to the UA, while which element controls certain break properties at a boundary is undefined in that level. These are distinct from invalid input and unsupported features. Keep all four statuses separate. Neither engine disagreement nor matching screenshots settles an underspecified case. [CSS Text line breaking](https://drafts.csswg.org/css-text-3/#line-break-property)

### Validation layers and generation limits

- WPT tests should link requirements and contain calibrated positive and negative controls. Preserve subtest identities, assertion execution, expected failures and platform conditions. A `rel=help` link provides traceability, not exhaustive coverage. [WPT CSS metadata](https://web-platform-tests.org/writing-tests/css-metadata.html)
- Cross-engine differential runs locate disagreement. Classify it as unsupported, discretionary, ambiguous or contradictory to a normative rule before calling it a bug. Consensus can reproduce a shared error.
- Metamorphic tests need proved or independently justified transformations. Splitting a text node, changing a cache history or replacing an expression with an equal serialization is not automatically semantics-preserving.
- Mutate shared classifiers, codecs, source extractors, observers and adapters as well as model branches. A mutation rejected only by a syntax error supplies no semantic sensitivity evidence. Retain the actual distinguishing observation and whether it is state-only or web-visible.
- Generate inventories, dependency candidates, grammar scaffolding, test skeletons and change alerts. Do not generate trusted semantics directly from prose or treat scraped grammar as all contextual restrictions. Webref distinguishes raw extraction from curated structural guarantees; neither establishes semantic correctness. Bikeshed's algorithm markup structures names and variables rather than providing executable semantics. [Webref](https://github.com/w3c/webref), [Bikeshed algorithms](https://speced.github.io/bikeshed/#algorithms)

## 4. Hard requirement trace: taint survives representation and history

### Normative endpoint and scenario

Consider a registered string custom property whose computed characters are identical whether obtained from a literal or an attribute, then substituted into a URL-taking value. The source matters: CSS Values marks attribute-derived values and containing functions as tainted; an arbitrary substitution's whole output inherits involved taint, including registered-property token equivalents. A tainted URL makes the declaration invalid at computed-value time. Nearby non-URL attribute use can remain valid, whereas wrapping the compound value in a custom-property substitution changes the propagation boundary. [CSS Values attr security](https://drafts.csswg.org/css-values-5/#attr-security)

**Spec-trace verdict: REACHED** for the tainted URL scenario under successful registration, attribute parsing and substitution. This verdict does not validate every animation/cache path. The same-payload literal control establishes that characters alone cannot represent the requirement. An invalid-at-computed-value-time declaration must then follow the relevant defaulting contract; the URL test observes the resulting `background-image`, not a guessed network request.

A concrete slice uses `CSS.registerProperty({name: "--picture", syntax: "<string>", inherits: false, initialValue: '"initial"'})`, an element with `data-image="picture.png"`, and `background-image: image-set(var(--picture))`. Compare `--picture: "picture.png"` with `--picture: attr(data-image)`. Calibrate literal image serialization independently; compare computed custom-property payloads before the URL assertion. For the history extension, use two constant keyframe endpoints and replace literal endpoints with attribute endpoints, then reverse the direction. This avoids using a disputed interpolation rule as the taint oracle. The retained executed probe uses a data URL instead of an external image resource.

### Required end-to-end joins

| Stage | Contract to prove or admit explicitly | Distinguishing challenge |
|---|---|---|
| DOM attribute and registration input | Element, namespace, selected registration and style epoch identify the actual inputs | Missing attribute, fallback, changed registration |
| Typed parsing and computation | Computed payload carries provenance through accepted type conversion | Same string via literal versus attr |
| Map insertion and inheritance | No-op equality preserves all downstream observations, not merely payload | Shared map with equal payload and opposite taint |
| Arbitrary substitution | Equivalent tokens retain whole-substitution taint at the specified boundary | Direct nearby attr versus whole compound value through var |
| Serialization and source spans | Byte ranges correspond to produced tokens, including empty output/separators | Touching untainted URL and tainted resolution spans |
| URL consumption and defaulting | Consumer sees the correct taint; rejection takes the correct computed-value path | Literal URL accepted, attr URL rejected |
| Temporal caches/effects | A retained computed object is observationally equivalent in every admitted future consumer context | Replace keyframes with equal characters but changed provenance |

For the model, use a value with payload and provenance, and a contextual relation that quantifies only over the admitted consumers. Do not require every native `PartialEq` to compare every field; require each optimization's chosen equality to imply the specific observation equivalence needed at that call site. This avoids both an unsound global equality assumption and an indiscriminate native equality change.

The local audit already supplies concrete warnings, not completion: root's map pair observed 78 PASS / 4 FAIL becoming 82 PASS; the adjacent-span diagnostic observed 1 FAIL / 4 PASS; the effect-replacement diagnostic observed 2 FAIL / 4 PASS with fresh/different-payload controls passing. The last two are separate repair leads at this report's freeze. Their source traces and retained receipts are hashed in `LOCAL-INPUTS.json`; this research did not rerun them or accept new native fixes.

The engine mapping crosses `Value::PartialEq`, map `do_insert`, cascade early-outs, substitution/`AttrTaint`, URL parsing and `KeyframeEffect::UpdateProperties`/animation equality. A proof of map count or payload interpolation cannot close these edges. Likewise, proof73's local frame theorem for unrelated flags cannot be promoted into a theorem that fresh-style recascade preserves those flags: that history model reused an abstract state whose native admission remained explicit.

**Acceptance gate for this pilot:** one independently reviewed normative contract; universal reference propagation and contextual no-op theorems; actual producer/consumer and temporal joins; exact source/pref bindings; calibrated tests for both directions of metadata change and span boundaries; a report that identifies any remaining representation or scheduler admission. Until all are present, publish the narrower component labels.

## 5. Spec-change exercise: display animation and inertness

Use a real historical semantic delta as a rehearsal, without claiming the intervening specifications differ only at this point. The July 2017 Display 3 draft marked `display` non-animatable. Current Display 4 specifies discrete animation with special behavior when one endpoint is `none`, and additionally derives inertness from the display value with animation/transition cascade origins ignored. [Display 3, July 2017](https://www.w3.org/TR/2017/WD-css-display-3-20170720/#propdef-display), [Display 4 animation](https://drafts.csswg.org/css-display-4/#animation)

HTML inertness affects interaction, including hit testing, selection and focus; it is not the same observation as absence of a box. This adds a host-standard dependency to the migration. [HTML inert subtrees](https://html.spec.whatwg.org/multipage/interaction.html#inert)

Run this exercise on two isolated profiles, retaining both:

1. **Requirement ledger:** replace the old animation-type requirement with separate obligations for general interpolation, the `none` exception and inertness. Record normative revisions and supersession; classify editorial anchor changes separately.
2. **Definitions:** add a display interpolation relation and a separate underlying-cascade observation for inertness. Keep box generation, animated display and interactive state distinct. State supported progress/numeric domain, effect composition and host dependencies.
3. **Proofs:** invalidate the old non-animation claim in the new profile. Prove the new endpoint/interior cases and compose box generation. The inertness proof needs an actual cascade-origin projection and HTML interaction contract; a theorem about interpolated enum values cannot substitute for it.
4. **Reference behavior:** create a distinguishing old/new example with base `inline` and keyframes `block` to `flex` sampled at 0.75. Separately test `none` to `block` at an interior progress to distinguish the exception from naive discrete interpolation. Then give an underlying `none` element an animated non-none value: its visual and inert observations must be modeled separately. These are proposed fixtures, not executed results.
5. **Gecko adapter:** inspect display animation, preference dispatch, cascade-origin computation, box reconstruction and interaction providers. Searchfox discovery located `impl Animate for Display` in `animated_properties.mako.rs`. The retained local excerpt shows a preference branch and endpoint-weight logic. It does not establish the inertness path or full conformance. Bind generated code, relevant configuration and actual callers before a native transfer claim.
6. **Tests and release:** pin WPT revisions; independently inspect supported assertions and add missing host-interaction observations. Replay old-profile behavior separately from new-profile behavior. Publish semantic migration notes and invalidate dependent source/refinement certificates even when Lean still compiles after a permissive API change.

The exercise passes only if the change detector identifies the cross-family obligations and the reviewers reject a deliberately incomplete “interpolation-only” migration. An automated textual diff is useful input; the semantic dependency closure remains a reviewed judgment. The retained display source excerpt is discovery evidence only, not a newly accepted source capsule.

## 6. Pilot sequence and measurable delivery gates

Do not estimate all CSS by multiplying the throughput of easy helper lemmas. Run these pilots in order of dependency, with independent work inside each accepted interface:

| Pilot | Purpose and required exit evidence |
|---|---|
| A. Contract infrastructure | Pinned profile, requirement IDs, assumption graph, reproducible checker and independently owned challenge contract; intentionally stale/omitted dependency rejected |
| B. Syntax to computed value | One complete public input path including malformed input/recovery, source positions, substitutions and defaulting; no supplied-token shortcut hidden in the claim |
| C. Metadata and temporal reuse | The attr trace above, including equal-payload replacement and empty/adjacent spans; source-to-history joins and negative controls |
| D. Layout boundary | A small but genuine inline-layout slice crossing writing mode, font metrics and fragmentation; explicit numeric and platform domain, environmental contracts and consumer observation |
| E. Evolution rehearsal | The display migration above, with old/new profiles, invalidated dependency closure, tests and adapter update; reviewer must catch omitted inertness |
| F. Family expansion | Reuse accepted interfaces for a new family, then compose it with an existing family and document every newly introduced premise |

For each pilot record actual person/agent effort, review waiting time, failed approaches, semantic revisions, source-adapter effort, provider admissions closed versus added, integration defects, replay cost and rework caused by a spec/source change. Separate reusable infrastructure from feature-specific work. Record attempted and rejected contracts as well as successful ones. Use observed ranges grouped by feature class to plan the next batch; there is no justified project completion date or coverage percentage yet.

Critical path: agreed interpretation → stable interfaces → independent reference → native provider/caller admission → cross-family integration → independent replay/release. Proof production can run in parallel after contracts stabilize. More producers cannot remove a blocked semantic decision, missing provider bridge or review bottleneck.

The main stop conditions are informative: if most effort moves assumptions into parameters, if integration repeatedly invalidates core types, or if tests discriminate models that the proofs cannot distinguish, pause breadth expansion and repair the relevant interface. Do not lower the approved contract to preserve throughput. A refuted obligation should become a retained counterexample plus a separately approved replacement target, not disappear from the ledger.

## 7. Standalone artifact and scalable ownership

Proposed package boundaries:

- `Profiles`: pinned requirement inventory, precedence and external-standard contracts.
- `Semantics`: neutral definitions and reviewed challenge statements; no Gecko source types.
- `Reference`: executable strategies and proved correspondence to the semantic relation.
- `Validation`: examples, WPT adapters, metamorphic contracts, mutations and result interpretation.
- `Adapters/Gecko`: exact source/extraction/provider/caller refinements and implementation-specific premises.
- `Releases`: locked dependencies, theorem inventory, assumption report and source-only replay instructions.

Avoid forcing Gecko's allocation strategy, enum layout or cache design into the semantic API. Conversely, do not erase those details from native refinement where they affect termination, rounding, ownership or observable behavior. Runtime code generation requires a separate compilation/execution trust statement even when the source-level Lean reference is proved.

Each requirement has an interpretation owner and an independent reviewer. Each adapter has a source owner; a separate integrator owns composition and release claims. Agents can scout specifications, propose contracts, implement proofs, produce reference tests and audit native callers in parallel, but an author cannot accept its own meaning or source correspondence. Review capacity should bound the active producer queue. Reviewers need complete small contracts and dependency summaries, not only expanding theorem counts.

Version profiles independently from library APIs and engine revisions. Any semantic change creates a new profile revision and migration record. API-compatible changes can still invalidate an interpretation certificate. Source changes may preserve a theorem only after a checked transfer; unchanged function bodies do not automatically preserve changed callers, providers or configuration. Preserve old releases and counterexamples. A CSSWG clarification should enter as an explicit decision with before/after examples, not a silent overwrite.

For release, authenticate inputs before executing helpers, rebuild from source in a fresh destination, check exact theorem/axiom inventories and independently owned contracts, replay relevant native/reference tests, and retain complete status identities. Generated targets can be removed after accepted reproducible replay; source, dependency locks, raw evidence and failure histories remain. This report's checker authenticates research files only—it does not implement that proposed proof pipeline.

## 8. Failure modes and completion decision

| Failure mode | Required response |
|---|---|
| Thousands of lemmas about a shared wrong classifier | Independent primitive/reference challenge and source mutation |
| “All CSS” means only successful well-formed declarations | Inventory error recovery, rejected declarations and public entry domains |
| Every subsystem chooses a different valid environment | Shared state/epoch contracts and whole-history composition |
| Layout equals a supplied geometry function | Expose the remaining layout obligation; do not count it closed |
| Browser tests pass through conditional skips | Track actual assertion prerequisites and separate support from pass |
| Equality proof forgets metadata or stale caches | Contextual observation and mutation histories |
| Weak theorem is renamed “refinement” | Independent challenge statement and explicit source/caller joins |
| Draft changes silently alter the target | Pinned profiles, reviewed semantic diff and dependency invalidation |
| More agent output outruns independent review | Limit work in progress; prioritize missing joins over new counts |

Recommended next deliverable: accept the pilot contracts and run A–C with the existing parsing/defaulting/taint work, while separately designing D's real layout boundary. Use E to measure maintenance rather than postponing it. Expand only after the measured review and composition costs are understood. A standalone research artifact can be useful throughout this process; the unqualified claim that all CSS or all Stylo is formally verified remains unsupported.
