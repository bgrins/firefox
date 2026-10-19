# Whole-CSS formalization: validation and delivery program

19 October 2026. Independent research track; proposed work, not newly implemented proofs or native acceptance. This extends the retained first roadmap. No production files, Git state, browsers or native builds were changed.

## Recommendation

Organize the project around reviewed semantic contracts and progressively complete, pinned profiles. Maintain two independent deliverables: a reusable CSS semantics/reference library, and implementation refinements such as Stylo adapters. A useful whole-CSS effort can start now; an honest completion claim requires a defined universe, explicit environmental contracts and closure of cross-module behavior. Neither a large number of Lean declarations nor many passing browser fixtures measures that closure.

Use the dated CSS Snapshot 2026 as the stable inventory starting point, supplemented by explicitly selected draft revisions and replacement rules. Snapshot inclusion describes stability, not implementation uptake. It does not make every editor draft a consensus requirement. [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/)

The previous local inspection recorded 127 feature records and 32 specification records, with full CSS conformance, mechanical prose translation and browser refinement all false. Those are historical inventory counts, not a denominator for progress. This research does not rerun or reaccept that library. General layout, fragmentation, shaping/font providers, painting, color, transforms, animation timelines, CSSOM and dynamic/cross-module native composition still require substantially more work.

## Preventing a large incorrect model

### Separate five questions

1. **Did we interpret the normative requirement correctly?** A domain reviewer traces the actual algorithm, guards, stage and object identity, including linked specifications, before consulting the implementation as an oracle.
2. **Does the model express that interpretation?** Another reviewer checks quantifiers, unsupported inputs, nondeterminism, invalid values, recovery, units and temporal observations. Keep alternatives and unresolved issues in the ledger.
3. **Are the model's claims proved?** Kernel-check the exact theorem inventory, audit axioms and transitive assumptions, and demonstrate nonvacuity. A proof can faithfully prove the wrong proposition.
4. **Does executable code implement the model?** Derive a relation between an independent specification and a reference algorithm. Native adapters need an additional relation and actual caller/provider admission.
5. **Do experiments challenge the claim?** WPT, model-based tests, cross-engine comparisons and mutations find errors; their finite success is not universal refinement.

Standard Lean axioms and native evaluation must be reported distinctly. The kernel does not authenticate an English interpretation, a Rust extraction script, a font library or an assumed scheduler. [Lean axiom documentation](https://lean-lang.org/doc/reference/latest/Axioms/)

For each assumption record its owner, consumer theorem, source evidence and discharge condition. For example, a helper that ORs one flag preserves unrelated bits in that supplied object; a subsequent fresh-style recascade may construct different unrelated flags. A history model that carries old bits forward has an additional frame assumption. Composition must never silently promote the local lemma into an engine-wide invariant.

### Independent review is an interface

A component submission should contain a short normative interpretation, definitions, independently stated reference relation, exact public theorem statements, assumptions and adversarial witnesses. Give the semantic reviewer the requirement and proposed observable contract first. Give the proof/admission reviewer the implementation and complete source map afterward. Require a separate reviewer for acceptance; agent identities alone do not guarantee independence if both copy the same unchecked classifier.

Review disagreement is useful evidence. Classify it as model error, implementation error, spec ambiguity, unsupported profile, provider discretion or harness error. Preserve the original target and counterexample. A weakened replacement gets a new identity; it does not retroactively close a refuted target.

## Validation layers and exit criteria

| Layer | Concrete acceptance gate | Common false success to reject |
|---|---|---|
| Requirement ledger | Every requirement in the release profile has an owner, source revision, interpretation status and dependency links | Counting spec headings or properties as requirements |
| Semantic model | Two reviews agree on inputs, failure modes, state and observations; alternative interpretations remain explicit | Encoding unresolved behavior as unconstrained nondeterminism |
| Universal proof | Exact theorem inventory and standard-axiom audit; all in-profile premises derived or visibly open; discriminating witnesses | A vacuous invariant or a component theorem replacing the requested endpoint |
| Executable reference | Soundness and completeness against a separately written relation, with declared determinism/discretion | Same unchecked lowering generates both sides |
| Browser validation | Calibrated resources, actual assertion completion, classified outcomes and source/binary/profile pins | Harness OK with missing subtests, or browser agreement treated as normative |
| Native correspondence | Complete relevant bodies/providers, source translation relation and caller construction of premises | A finite native matrix described as an all-input compiler proof |
| Release | Clean source-only replay, independent acceptance, precise claim/assumption inventory and migration notes | A passing old proof reused after a semantic spec edit |

WPT's testharness supports observable API assertions and explicit asynchronous completion. CSS metadata supplies specification links; those links identify relevant sources but do not establish assertion coverage. Use rendering tests when geometry or pixels are the intended observation, with controlled fonts, device scale and permitted tolerances. [WPT JavaScript tests](https://web-platform-tests.org/writing-tests/testharness.html), [CSS metadata](https://web-platform-tests.org/writing-tests/css-metadata.html)

### Differential, metamorphic and mutation checks

- Compare model results with at least two independent engine families where available. Check feature support first. Compare specified observations rather than incidental internal order or floating representation. An engine majority cannot settle the standard.
- Derive metamorphic transformations from the model. For example, alpha-renaming custom-property names is valid only when every definition/reference/registration and relevant observation is renamed consistently. Inserting a DOM wrapper is not generally inert: inheritance, selectors, containment and layout can change. Text-node partition invariance also needs its actual scope established; our project has retained counterexamples to overbroad forms.
- For each theorem family, compile semantic mutants that violate a relevant guard, coordinate, ordering, identity, flag or publication step. Require a meaningful witness failure, not a compiler/import error. Mutate observation adapters and shared primitives as well as implementations.
- Keep a compact challenge corpus covering premises, boundary conditions and discovered counterexamples. Increase it to address a concrete remaining risk; do not grow counts as a substitute for closing a universal dependency.
- Store complete keyed observations, including errors and partial publication, not only a Boolean agreement. Normalize only what the spec permits, and document that projection.

## Generation and extraction limits

Webref can populate property/grammar/IDL/reference inventories; its raw and curated outputs have different structural guarantees. Bikeshed provides document structure, definitions and algorithm/variable markup. Neither supplies a full mathematical interpretation of normative CSS prose. [Webref](https://github.com/w3c/webref), [Bikeshed algorithms](https://speced.github.io/bikeshed/#algorithms)

Generate stable identifiers, dependency candidates, source-change alerts, typed metadata, theorem skeletons and test scaffolding. Each generator should have a supported input grammar and explicit rejection behavior. A certificate or kernel-checkable output is preferable to trusting generated conclusions. Handwritten facades must enumerate substituted operations, failure behavior and observable effects.

Do not automatically infer semantics for prose exceptions, compatibility rules, invalid-at-computed-value-time behavior, percentages, font metrics, asynchronous scheduling or platform limits. Do not treat an unchanged function name/hash subset as proof that its callers/providers remain compatible. Full source bodies, external state and configuration also belong to the admission record.

## Worked update: custom-property computed-style enumeration

This is a proposed migration exercise grounded in an actual specification change, not a claim that the migration has been implemented.

The dated 2016 CSSOM getComputedStyle algorithm describes a declaration list of supported longhands. The dated 2021 algorithm additionally includes custom properties whose computed values are not guaranteed-invalid; its change history explicitly records custom-property inclusion. We isolate this change from other changes between those drafts, using connected same-document ordinary elements without pseudo-elements. The current editor draft retains that custom-property condition. [2016 CSSOM](https://www.w3.org/TR/2016/WD-cssom-1-20160317/#dom-window-getcomputedstyle), [2021 CSSOM](https://www.w3.org/TR/2021/WD-cssom-1-20210826/#dom-window-getcomputedstyle), [current CSSOM](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle)

| Step | Required artifact and change |
|---|---|
| Detect and interpret | A reviewed semantic-change record compares the two dated clauses and their definition of supported properties. Preserve both profiles; record this as a semantic addition, not an editorial anchor move. |
| Requirement ledger | Add/version `cssom.computed-style.custom-enumeration`, linked to custom-property computed values, guaranteed-invalid state, declaration lists, length and indexed access. Record that custom-property order is unspecified. |
| Model | Represent absent/guaranteed-invalid separately from a valid empty token sequence. Define allowed custom enumeration as every effective non-invalid name exactly once, with any permitted order. The model uses semantic maps, not Gecko tombstones. |
| Theorems | Prove membership iff the effective value is non-invalid, uniqueness, count/list consistency, valid-empty inclusion, and absence after reset. Compose these with computed-value resolution under its explicit premises. Do not assume the map already satisfies the property being proved. |
| Reference behavior | Extend the old reference's longhand-only projection with a filtered unique semantic custom-name list. Retain the old reference for its historical profile. Compare new results modulo allowed order. |
| Distinguishing test | A connected element with `--x: 20px` adds one custom name in the new profile; a reset to initial removes it; a valid empty value remains listed. Pair with no-property and inherited-value controls. |
| Gecko adapter | Bind actual cascade/defaulting, persistent map lookup, count, iteration, indexed lookup and CSSOM publication. Prove tombstones mask ancestors; distinguish effective Some count from stored-key count; derive indexing bounds. A correct value getter alone is insufficient. |
| Release review | Revalidate every consumer of count/enumeration and every theorem using its former meaning. Mark native closure open if Arc/container/caller/usize obligations remain; release semantics separately if appropriate. |

The empty-value distinction comes from CSS Variables: guaranteed-invalid serializes empty, while a valid empty token sequence is different. It follows that filtering on serialized string emptiness is not an admissible implementation of the new rule. [CSS Variables guaranteed-invalid values](https://drafts.csswg.org/css-variables/#guaranteed-invalid-value)

Our current source investigation provides a concrete warning: native count, nearest-owner lookup and iterator output can disagree. An ancestor-duplicate correction can expose an independently incorrect tombstone count. The associated proposals remain separate from this research; no unexecuted diagnostic is promoted to a confirmed defect here. The example's required universal bridge must cover both contracts before claiming correct CSSOM publication.

This exercise can be completed using dated specifications; the attempted GitHub PR4948/API retrieval was unavailable during this track. No merge date or exact PR diff is claimed. A release migration still must archive authenticated normative fragments/revisions and their dependency definitions; this research's URL ledger is not that proof-input archive.

## Staged program and parallel work packages

| Stage | Work packages that can proceed in parallel | Critical dependency and exit gate |
|---|---|---|
| A. Establish the universe | Spec inventory/replacement map; requirement schema; existing-library claim audit; toolchain/replay policy | Agree on a named profile, boundaries and status vocabulary before reporting coverage. Every imported normative dependency has a disposition. |
| B. Establish shared semantic interfaces | Tokens/components; values/units/errors; DOM/environment identities; state/effects; reference observation format | Independent review settles the interfaces before many dependent modules proliferate. Add a small cross-module example to detect mismatched contracts. |
| C. Close one vertical slice | Semantic proofs; independent reference; browser challenge corpus; one exact Gecko adapter | Raw admitted input through the advertised observable outcome, with transitive premises accounted for. Native acceptance is a separate gate. |
| D. Prove maintenance | Historical semantic-update exercise; change-impact tooling; outside replay/review | Demonstrate old/new profiles, distinguishing behavior, migration of affected proofs and an external replay. |
| E. Expand connected families | Multiple specification families with dedicated reviewers; provider adapters; interaction audits | Each addition must close or explicitly extend shared contracts. Prioritize dependencies that block several endpoint claims. |
| F. Release and sustain | Profile audit; reproducibility/package work; cross-engine validation; maintenance queue | No in-profile requirement silently unsupported. Publish exact remaining external assumptions, failed targets and spec/version limitations. |

A practical team can have a prose/specification owner, semantic-model author, independent proof/admission reviewer, and validation/native-adapter author working concurrently on agreed interfaces. Rotate review ownership and permit rejection without changing the producer's scope. A separate integration owner resolves cross-module contracts and maintains the claim ledger. Adding authors beyond review/integration capacity creates unreviewed models faster; it does not shorten the critical path.

The central dependency is: agreed interpretation → shared observations and representations → substantive local proofs → caller/provider composition → endpoint claim. Tests, extraction tooling and inventories can progress beside it, but cannot bypass unresolved interpretations or supply missing universal premises.

## Estimation method and risks

Estimate after sampling representative work, not by multiplying the number of properties by an optimistic average. Sample at least a grammar/recovery component, computed-value/cascade interaction, layout algorithm with metric providers, and temporal/CSSOM feature. Record separately:

- interpretation/review effort and unresolved CSSWG dependencies;
- model/proof construction and independent review effort;
- provider/caller admission effort, including native arithmetic and failure paths;
- adapter/test/calibration work and source-only release effort;
- rework after counterexamples and dependency changes.

Build a dependency graph of work packages. Use observed effort ranges by class and distinguish total work from critical-path elapsed time and reviewer capacity. Treat unresolved semantics and platform-provider modeling as explicit uncertainty, not zero-cost tasks. Re-estimate after each accepted vertical slice and semantic-update exercise. Measure accepted endpoint claims and discharged premises, review turnaround, rework and spec-change lag; do not infer an all-CSS percentage from theorem or fixture counts.

Major risks are shared mistakes in model/reference code, informal prose ambiguity, unrealistic numeric/metric abstractions, version drift, asynchronous state omitted from value-only models, and component contracts that fail to compose. Mitigations are the independent review and release gates above. Native compiler/heap/platform verification is an additional research commitment; state clearly whether the advertised profile assumes those interfaces or proves them.

## Standalone release contract

Ship a small `Spec` package with declarative relations, a `Reference` package with executable correspondence, a `Validation` package with traceability and challenges, and separate versioned engine adapters. Consumers should be able to replay a semantic module without a Firefox checkout. Public APIs and spec-profile versions are independent: a semantic change can require a new profile even when Lean types remain unchanged.

Each source-only release includes exact spec/toolchain/dependency identities, source/licensing provenance, theorem/axiom inventory, independent reviews, runnable examples, negative/refuted results, input restrictions and migration notes. Generated targets may be discarded after successful replay; retained sources and receipts may not. Unsupported behavior is an explicit result, never silently interpreted as invalid CSS or an empty value.

Whole-CSS semantic modeling is a plausible sustained research program. Complete Stylo conformance is a larger claim requiring actual implementation and host composition. This plan establishes acceptance gates for increasing those claims; it supplies no invented deadline, coverage percentage or blanket completion promise.
