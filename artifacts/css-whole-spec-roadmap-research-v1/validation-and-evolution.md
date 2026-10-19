# Validating and maintaining a CSS specification model

Research track 3; 19 October 2026. This is a proposed research and maintenance plan, not new proof acceptance. Primary web sources were checked during this task. Local inspection hashes are in `validation-evidence/local-inspection.json`.

## Recommendation

Build an independently useful, versioned CSS semantic library with a maintained requirement ledger, reviewed interpretations, executable reference algorithms and kernel-checked correspondence. Keep browser implementation refinements in separate adapter packages. Aim for a complete **named, pinned profile** at each release, while expanding the profile toward the whole specification set. Do not advertise an unqualified percentage or completion date for “all latest CSS.”

A comprehensive formal model is a plausible long-term research objective. It does not follow that arbitrary English prose can be translated faithfully by a model or that proving facts about the result verifies Stylo. The hardest recurring work is choosing the correct semantics, resolving ambiguities, and deriving the provider/caller premises needed to connect components. AI agents can accelerate all three, but a successful Lean proof certifies the stated proposition rather than its interpretation of a standard.

CSS is a family of specifications with overlapping levels and external dependencies. The CSS Snapshot groups modules by stability rather than browser adoption and explicitly says included specifications can still change. Therefore “current CSS” needs a manifest of exact versions and replacement relationships, plus an explicit policy for experimental drafts. [CSS Snapshot 2026, 22 June 2026 Note](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/)

## What the current project already has

The local standalone `css-spec-lean/coverage.json` declares 127 feature records and 32 specification records, with `full_css_conformance`, `mechanized_prose_translation` and `browser_refinement` all false. These are inventory counts, not requirements covered or percentages. Its accepted coverage map separates universal relations, finite kernel examples, browser comparisons and reproducibility.

The existing library has useful compositional machinery for scoped selectors, token/component syntax, cascade/defaulting, closed property computation and selected source-to-style profiles. Its explicit remaining boundaries include general layout, shaping/fonts, painting, colors, transforms, animation timing, CSSOM, dynamic environments and native adapters. Some headings retain historical limitations, so a new inventory must reconcile feature records and acceptance reports rather than infer absence from one sentence.

The implementation-side `FORMAL-CLOSURE-CHECKLIST.md` also preserves refuted partition/locality targets and unresolved provider/temporal contracts. That discipline should become part of the public artifact. Component counts cannot discharge an open endpoint theorem. For example, the recently reviewed explicit-inherit value theorem does not establish substituted-inherit invalidation: correct initial values can coexist with a missing dependency flag. A semantic model needs values **and** the relevant temporal observations when its claim includes browser evolution.

## Completion criteria: independent dimensions, not one score

| Claim | Required evidence before using the word complete | What remains separate |
|---|---|---|
| Inventory complete for a release profile | Every normative requirement in the pinned module set is classified; imported requirements, overrides, normative tables and algorithms are reconciled; exclusions and unresolved interpretations are explicit | No claim the requirements have been modeled |
| Semantic model complete for that profile | Reviewed definitions represent every classified behavior, failure/recovery case, environment choice and cross-module interaction; allowed nondeterminism is represented; no unsupported path silently returns a valid value | Prose-to-definition interpretation remains a reviewed trust boundary |
| Executable reference complete for that model | Totality/progress where required, plus soundness and completeness against independently stated relations; executable outcomes distinguish invalid, unsupported and permitted nondeterminism | A reference algorithm can be impractical; this does not verify an engine |
| Verification target complete | Every selected theorem and its transitive premises are proved or exposed as genuine external interfaces; no requested obligation is dropped after a counterexample; nonvacuity and exact axiom audit pass | There is no meaningful claim to have proved every possible property of CSS |
| Browser validation complete for a stated test plan | All mapped runnable tests and calibrated differential fixtures have classified results, exact source/binary/profile identity and no unresolved harness failures | Finite tests do not become universal proofs; engine agreement is not normative authority |
| Implementation refinement complete for a pinned component | Exact executable source and providers refine the semantic model over the stated admitted inputs, including state, effects, failure paths, resource limits and relevant numeric behavior; caller admission is derived | Whole compiler/runtime/OS trust and other engine components may remain outside |
| System-level CSS conformance claim | Cross-module and temporal composition is closed for all inputs in the advertised profile, with external contracts explicit and validated; every remaining gap is outside that advertised profile | “All CSS in a deployed browser” additionally involves host behavior, platform providers and implementation constraints |

Assumptions also need owners and levels: helper inputs, provider outputs, caller construction, temporal scheduler and native representation. Record the exact theorem that consumes each assumption and what would discharge it. In proof73, the local flag OR preserves other bits in the supplied state; the history model's reuse of `otherFlags` is a model-frame admission. A real fresh-style recascade may reconstruct different unrelated flags. A helper frame theorem must not silently become a theorem that the engine preserves those bits across recascade.

These dimensions should appear independently in reports. A module can have complete declarative semantics but no executable interpreter; a narrow native repair can be well validated while its original broader proof target remains refuted. A complete pinned model can represent UA discretion as a relation over permitted results. An unresolved disagreement about what the prose permits must remain an interpretation issue, not be silently converted into discretion.

## What can be generated safely

Use existing standards machinery as **input indexing and change detection**. Webref provides extracted CSS/IDL/definition/reference data. Its raw branch explicitly lacks validity guarantees; curated data applies maintained corrections and provides stronger structural guarantees. Even curated output is not an executable account of all normative prose. [Webref](https://github.com/w3c/webref)

Bikeshed names and scopes prose algorithms and their variables, and supplies definitions, links and structured document markup. That improves extraction and traceability. It does not assign a mathematical denotation to every English step. [Bikeshed algorithms](https://speced.github.io/bikeshed/#algorithms)

| Automate with checks | Require semantic review or a separate proof |
|---|---|
| Pin source revisions, URLs, anchors, definition names, property tables and grammar text | Decide which level replaces which earlier requirement and what prose exceptions mean |
| Generate typed identifiers, metadata inventories and parser skeletons from reviewed schemas | Interpret context-sensitive grammar, recovery, computed-value stages and serialization |
| Detect changed requirements and traverse an overapproximating dependency graph | Judge whether a prose edit is editorial or changes the relation |
| Generate theorem stubs, exhaustive finite enum checks and test templates | Choose meaningful invariants, correct premises and independent reference semantics |
| Run kernel/audit/replay gates, shrink counterexamples and label unsupported inputs | Decide whether an engine discrepancy is a browser defect, model error, test error or spec ambiguity |
| Draft proof terms and native extraction adapters | Establish that extracted bodies, facades and providers preserve the actual behavior being claimed |

Generation is most trustworthy when it produces proof obligations or independently checkable certificates. Avoid generating both the implementation and “reference” from the same unchecked classifier. Our shared codec/unit-classifier boundaries show why two agreeing computations can share the same mistake. Grammar extraction does not by itself establish that generated parsing respects all surrounding prose restrictions.

## Requirement-to-evidence traceability

Extend the current coverage schema with stable requirement IDs. IDs should survive section moves but point to the exact historical source hash. Use many-to-many links rather than one theorem per section:

```
requirement: values5.substituted-css-wide
spec: {revision, source_path, section_anchor, fragment_hash, normative_context}
interpretation: {review_record, alternatives, unresolved_issue_ids}
profile: {host_modes, supported_syntax, environment_contracts}
model: {definitions, observations, input_admission}
proof: {theorems, transitive_premises, axioms, independent_review}
reference: {algorithm, equivalence_theorem}
validation: {WPT_ids, oracle_trace, controls, source_and_binary_pins, outcomes}
implementation: {adapter_revision, exact_bodies, providers, refinement_status}
status: modeled | conditional | closed | refuted | ambiguous | unsupported
```

A validator should reject missing links, stale hashes, mismatched profiles and a theorem marked closed while depending on an open in-profile admission. It should preserve the original target and failed witness when a claim is refuted. A repaired or weaker claim gets a new identity and an explicit relation to the old one.

WPT already expects CSS tests to identify relevant specification sections and provides optional/required-behavior metadata. Reuse `rel=help` links as discovery hints, then associate the exact assertion and oracle with requirement IDs. A file-level link is not a completeness certificate. Browser expectation metadata is a separate execution policy: no `.ini` entry is not evidence that a test was actually run or passed. [WPT CSS metadata](https://web-platform-tests.org/writing-tests/css-metadata.html)

## Validation strategy

1. **Interpretation review:** independently trace the normative call chain and guards before reading the proposed implementation as the oracle. Review quantifiers, stage, object identity, environment ownership, invalid-input handling and allowed choices.
2. **Model checks:** prove independent reference/algorithm correspondence, totality or appropriate liveness under explicit assumptions, preservation and composition. Include reachable witnesses showing the premises are satisfiable and the theorem rules out the intended error.
3. **Source admission:** retain complete relevant native definitions and provider/caller records. Either prove a supported-language translation or clearly label a manually reviewed abstraction. An exact extraction plus finite correspondence is useful evidence, not automatic universal refinement.
4. **Differential tests:** execute the model and at least independent browser engines on identical admitted inputs. Compare specified observable projections: values, CSSOM, geometry or event traces. Calibrate fonts/metrics and capture asynchronous completion. Reject unsupported inputs rather than coerce them into a negative answer. Majority voting cannot settle a spec interpretation.
5. **Mutation tests:** target each semantic obligation independently: guards, coordinates, flags, reset/order, provenance and provider assumptions. Require the mutant to compile and reach the intended semantic rejection; an import error is not success. Mutate adapter observations too, so a shared wrong encoding/classifier is not invisible.
6. **Reproducibility:** authenticate all executable dependencies before imports, replay from a manifest-only source copy with explicit toolchains/environment, retain raw outputs and exact theorem inventory, and test tamper rejection. Generated build outputs need not be vendored or retained after accepted replay; sources and receipts do.

Preserve discrepancy triage as data: model mistake, implementation defect, specification defect/ambiguity, unsupported profile, numerical discretion, or harness failure. Cross-engine evidence is especially valuable for exposing a mistaken interpretation, but no browser should define the spec by accident.

## Keeping up with CSSWG changes

Maintain two tracks: a reproducible stable profile and an experimental draft profile. Pin the source revision, generated HTML or source fragments, Webref revision, grammar extractor version and dependency map. Merely storing a live URL is insufficient.

An update job should fetch a candidate revision, compare normative fragments/tables/references and then propose an affected-requirement set. Include callers and imported definitions, not only text directly inside the changed anchor. Rebuild affected definitions, proofs, examples and browser fixtures, followed by a clean full-profile replay at release. A passing old proof after a prose change does not establish that the definition was updated correctly: require an interpretation review and a distinguishing old/new witness for semantic changes. If the change is editorial, retain the reviewed equivalence justification.

When the model exposes ambiguity, preserve competing interpretations and a minimal trace/test. Prepare a CSSWG issue with precise source version, relevant algorithm calls, browser outcomes and proposed clarification. The CSSWG contribution process uses issue discussion and group consensus for substantive changes; our model should track that outcome rather than declaring its own interpretation normative. Draft the issue internally first; publishing is a separate authorized action. [CSSWG contributor guidance](https://github.com/w3c/csswg-drafts/blob/main/CONTRIBUTING.md)

## Standalone artifact governance and API

Proposed package boundaries:

- **CssSpec:** implementation-independent data and declarative semantics, with versioned profiles and explicit environmental contracts.
- **CssReference:** executable algorithms with correspondence proofs and a stable machine-readable observation format.
- **CssValidation:** traceability registry, WPT/model adapters, differential corpus and mutation/replay tooling.
- **GeckoRefinement:** separately versioned native source bindings, admitted representation interfaces and proved transfers. Other engines can implement their own adapters.

Keep frontend parsing/DOM acquisition and host fonts/Unicode/time/resource policies explicit; do not inject Firefox quirks into the neutral semantics. Unsupported behavior must be distinguishable from invalid CSS and from an allowed empty result.

Use semantic versioning for public APIs, plus an independent spec-profile ID containing source revisions. A spec semantic change is visible even when the Lean signature is unchanged. Preserve older profiles and counterexamples; do not rewrite sealed evidence. Releases should publish source-only archives, license/provenance inventory, a claim matrix, dependency/axiom report and migration notes. Deduplicate identical vendored inputs by content where practical without replacing a pinned dependency with a live workspace lookup.

Require both semantic-domain review and proof/admission review for a new normative claim. Agents can do drafting, search, proof iteration and checks; no agent should approve its own interpretation by citing its own tests. Human/editor review is particularly important for layout, compatibility behavior and unresolved standards questions. External researchers should be able to replay a small module without obtaining or building Firefox.

## Prior art and what transfers

| Primary source | Relevant precedent | Limit |
|---|---|---|
| [Cassius repository](https://github.com/uwplse/Cassius) and [OOPSLA paper](https://sandcat.cs.washington.edu/papers/Torlak-cassius-oopsla-2016.pdf) | A logical layout model and solver-based reasoning, validated against captured browser results | Explicit CSS 2.1 fragment; not an all-CSS Lean library or engine refinement |
| [CSS Minification via Constraint Solving](https://arxiv.org/abs/1812.02989) | Formal selector/dependency semantics used to justify transformations | A scoped optimization problem, not general CSS rendering |
| [JSCert](https://www.doc.ic.ac.uk/~pg/publications/Bodin2014Trusted.html) | Coq semantic specification, a separately proved reference interpreter and conformance testing | JavaScript ES5-era work; useful methodology rather than reusable CSS semantics |
| [JISET](https://pure.kaist.ac.kr/en/publications/jiset-javascript-ir-based-semantics-extraction-toolchain/) | Extraction from structured ECMAScript grammar/algorithms plus manually completed gaps | Does not demonstrate automatic correct translation of CSS prose into Lean |
| [WebSpec](https://arxiv.org/abs/2201.01649) | Coq browser-interaction model, invariant analysis and executable counterexample traces checked in browsers | Browser security mechanisms; not a CSS/layout formalization |

A bounded primary-source search did not establish an existing comprehensive CSS-to-Lean specification translation. That is not a proof that none exists. The concrete prior art above supports a reviewed semantic model plus executable/differential validation, not a claim that a prose converter can remove semantic judgment.

Lean's kernel and axiom audit provide a strong proof boundary, but the trusted base still includes definitions and admitted interfaces. Native evaluation adds compiler trust; current Lean documentation distinguishes it from ordinary kernel-checked proof reduction. Publish the exact per-theorem axiom inventory and toolchain, and segregate native-evaluation evidence if used. An external checker can further diversify kernel validation, but does not verify prose interpretation or C++/Rust source correspondence. [Lean axioms](https://lean-lang.org/doc/reference/latest/Axioms/), [proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)

## Concrete roadmap for this track

1. **Make the claim ledger enforceable.** Convert existing coverage/admission records into requirement IDs and separate completion dimensions. Pilot on substitution, cascade/defaulting and one selector family. Exit: no unsupported path or open premise is mislabeled closed; all public claims point to exact evidence.
2. **Close a vertical reference profile.** Choose raw CSS plus a specified DOM/environment profile through computed values, including invalid input and mutation events. Exit: the end-to-end theorem states the actual entry and observations, not merely an internal token list. This is a deliberately scoped milestone, not a replacement of the whole-CSS objective.
3. **Prove evolution works.** Process an actual historical semantic spec change through old/new profiles, a distinguishing witness, affected theorem migration and WPT mapping. Exit: reviewers can reproduce both versions and see exactly why claims changed.
4. **Add cross-engine validation and outside review.** Publish the standalone package and small executable fixtures. Exit: a separate team can interpret, run and challenge it; all discrepancies are classified without silently changing admissions.
5. **Expand by connected semantic families.** Require each new family to discharge shared interfaces or explicitly extend them, including temporal effects and external providers. Prioritize gaps blocking composition over additional repetitive finite cases.
6. **Attempt complete pinned releases.** Audit every in-profile normative requirement and cross-module interaction. Increase the profile toward the chosen CSS specification universe while retaining a separately honest engine-refinement ledger.

I would not promise that all modern CSS or all of Stylo will be verified on a short autonomous run. The useful near-term success criterion is a reusable research artifact whose precise claims grow, whose assumptions shrink, and whose source/spec changes can be revalidated without losing historical evidence.
