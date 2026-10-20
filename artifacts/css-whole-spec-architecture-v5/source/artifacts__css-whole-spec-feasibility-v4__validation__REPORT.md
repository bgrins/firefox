# Whole-CSS validation: an adversarial release program

Research recommendation, 2026-10-19. This extends the [v3 validation report](../../css-whole-spec-feasibility-v3/validation/REPORT.md): the new contribution is a minimum release design, challenges to the v4 prototypes, and a concrete spec migration that changes a shared interface. No new CSS proof, browser result or engine conformance claim is made here.

## 1. What to build first

Build a standalone, deliberately partial CSS semantics package. A release must identify its normative profile, input domain, observations, allowed choices, theorems, and transitive assumptions. Reserve “whole CSS” for a reviewed normative universe with its host dependencies and residual older rules accounted for. A large property catalog or theorem inventory cannot establish that universe.

Keep three independently releasable claims:

| Claim | Required evidence | Does not establish |
|---|---|---|
| Interpreted model | Independently reviewed prose-to-contract trace; universal theorems over admitted inputs; explicit choices and counterexamples | That the interpretation captures every applicable rule |
| Executable reference | Total execution or specified divergence/error behavior; refinement to the model; exact input/output representation and provider contracts | That a browser implements it, or that an unsupported input is invalid CSS |
| Engine adapter | Source revision, complete caller/provider admission, state representation and observable refinement; bounded runtime evidence labeled separately | Other engine revisions, platforms or undisclosed assumptions |

Publish a conditional claim when a boundary remains. A local flag-preservation theorem cannot become a theorem about fresh-style reconstruction merely because the caller imports it. Each assumption needs an owner, the exact interface/phase where it is introduced, and a consuming theorem. Dependency closure must retain its status.

### Minimum repository

```text
lean-toolchain, lakefile.lean, lake-manifest.json
profiles/       pinned documents, requirements, exclusions, change decisions
Css/Interfaces/ typed states, providers, observations, choice protocols
Css/Semantics/  declarative relations and independently reviewed contracts
Css/Reference/  executable algorithms and refinement proofs
contracts/      independently authored challenges and nonvacuity witnesses
validation/     small cases, WPT mappings, differential receipts, reducers
adapters/gecko/ separate optional package with exact source bindings
releases/       claim manifest, theorem inventory, axioms, assumptions, replay
```

The core must check without a Firefox checkout, browser, network or retained build directory once declared toolchains/dependencies are supplied. Pin dependency source and tool versions; retain provenance/licenses. Make generated outputs disposable. Keep browser/native tools outside the Lean package's trusted path. Use one small versioned observation format; do not introduce a framework for every family before the first composed example works.

A release manifest binds profile and interface digests, exact theorem names, transitive axiom inventory, source inputs, and commands. Kernel checks need statement review: Lean's documentation explicitly separates checked proofs from the intended meaning of their statements, and describes axiom audits and fresh proof rechecking. [Lean validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## 2. Independent challenge of the v4 drafts

I read the captured inventory schema/result, both semantic prototype modules, and both peer reports. Their exact reviewed bytes are retained in `evidence/`; I did not execute them or independently accept their final packages. The inventory report was announced finalized; semantic files were captured during coordination.

**Inventory:** named requirements, contract digests, interface revisions, observation IDs, residual supersession, and separate claim levels are useful release infrastructure. The producer's result explicitly leaves whole-CSS completion false. Its synthetic accepted fixture tests the gate, not CSS coverage.

The semantic boundary remains external: a source-unit row can omit an exception, an `accepted` predicate can be false for every useful input, and an evidence path can point at a proof of the wrong proposition. The demo checks propositional guards over a bounded atom set; satisfiable atom assignments do not establish realizable CSS environments. Require reviewed certificates for nonempty domains, permitted-choice consistency, exclusions and dependency cycles. The current demo conservatively blocks cycles; certificate support is a future extension. Cycles are not automatically errors: an accepted simultaneous/fixed-point proof may discharge a strongly connected component. Merely finding all its internal edges does not.

**Semantic protocol:** `actual_footprint_sufficient` gives a useful conditional result: agreement on requests actually visited preserves this pure plan's result and trace. The clients distinguish phases and epochs, retain unsuccessful requests, and demonstrate that a single provider cannot return different answers to the same key within one episode. These are meaningful architecture checks.

They leave actual CSS key construction, episode boundaries, mutable provider admission and numeric domains open. Finite `Plan` construction must not assume away CSS cycles or termination obligations. The example arithmetic over `Nat` is a restricted prototype. A real caller must derive owner/epoch/phase identities and consistent answers; providing an independently plausible answer for each query is insufficient.

**Release decision:** adopt these interfaces as pilot candidates. Do not promote either prototype's structural/theorem results to a coverage claim. Add the following challenges before accepting the first composed pilot.

## 3. Worked adversarial acceptance: clipping is not scrolling

### Normative trace and independent oracle

Scenario: an active standards-mode document with an ordinary non-root, non-body block; a 100-by-100 CSS-pixel padding box containing a 300-by-300 child; no border, padding, transforms, snap, smooth scrolling, writing-mode reversal or anchoring disturbance; initially zero scroll offset. Compare `overflow: hidden` and `overflow: clip`.

1. Overflow defines hidden as clipped but programmatically scrollable; clip disallows scrolling. It also distinguishes the formatting-context effects. [Overflow 3, overflow values](https://drafts.csswg.org/css-overflow-3/#overflow-properties).
2. The `scrollTop` setter normalizes its argument, checks document/window/root/body and box prerequisites, then scrolls an eligible element. The getter exposes the resulting coordinate; no-box and special-root cases have separate behavior. [CSSOM View, scrollTop](https://drafts.csswg.org/cssom-view/#dom-element-scrolltop).
3. Under the stated ordinary-box premises, assigning 20 should expose 20 for hidden and retain zero for clip. This is a proposed independent test oracle, not a test executed in this research.

**Verdict: REACHED for this restricted spec scenario.** Root/body, inactive-document and no-box routes are excluded by explicit prerequisites, not erased from the full requirement universe. They must be separate requirements/controls before widening the claim.

A tempting wrong model reduces both values to a Boolean “clips.” It can prove identical initial pixels and even show two implementations agree if both share that Boolean. It loses the API distinction. This is a concrete case where many true Lean statements would cover too little CSS.

### Required proof and observation chain

| Boundary | Required contract |
|---|---|
| Syntax/cascade | Which value reaches the computed style; property/defaulting and current profile are explicit |
| Layout | Correct box, padding geometry, overflow extent and readiness for this element |
| Overflow | Clipping region and scrolling capability are distinct observations, with axis identity |
| CSSOM action | Correct document/box branch, normalized input, permitted offset and effect ordering |
| History | Write followed by read observes the same element and updated episode |
| Gecko adapter | Actual entry, layout flush, scroll-frame selection and final read implement those contracts |

Searchfox discovery locates `Element::SetScrollTop` in `dom/base/Element.cpp` and generated Element bindings. That is an adapter starting point only; this research has not inspected the full native call chain or established its refinement.

An independent interpreter writes the scenario, branches and expected observations before reading the model. Another reviewer checks the exception routes and numeric prerequisites. The proof producer then supplies the model and execution. Shared primitive classifiers must receive their own audit; the reference must not merely call the implementation under another name.

### Deliberate rejection tests for the pilot

| Deliberate defect | Acceptance gate that must reject it |
|---|---|
| Collapse hidden/clip to clipping Boolean | Independently authored write/read observer contract |
| Admit no actual boxes by a false precondition | Concrete inhabited scenario plus reviewed domain correspondence |
| Return `Unsupported` on all inputs | Declared-domain totality and explicit unsupported disposition |
| Delete the CSSOM dependency and retain pixel tests | Reviewed observation roster and dependency contract digest |
| Read another element or stale epoch | Identity/history witness and caller-derived provider keys |
| Reuse the old mixed-axis normalization after a spec update | Versioned migration fixture and invalidated interface binding |

These are proposed mutation gates, not reported executions. Mutants must reach the intended semantic assertion; syntax failures do not count. A passing finite mutation suite strengthens diagnostics but cannot prove prose completeness.

## 4. Real evolution exercise: axis-specific scrolling

The dated 7 October 2025 Overflow 3 draft changes a specified `clip` to computed `hidden` when the opposite axis has a scrollable value. [Dated Overflow 3 draft](https://www.w3.org/TR/2025/WD-css-overflow-3-20251007/#overflow-properties).

The current draft retains clip in that mixed combination and defines single-axis scroll containers. Its change log points to issue 12289. The issue's resolution explicitly asks for review of consumers affected by a nonscrollable axis. [Current Overflow 3 changes](https://drafts.csswg.org/css-overflow-3/#changes), [CSSWG issue 12289](https://github.com/w3c/csswg-drafts/issues/12289).

Use this as the first maintenance rehearsal:

1. Preserve the old profile and its claims. Pin the new document and editorial change separately; an issue label or module level alone does not identify normative authority.
2. Split the changed requirement from unchanged hidden/hidden and clip/clip behavior. For `overflow-x: scroll; overflow-y: clip`, the two profiles expect different computed y values. Keep both expectations with their profile IDs.
3. Replace any inadequate one-bit scrolling interface with per-axis capabilities, while retaining box-level properties where appropriate. Classify this as a semantic interface change, even if a Lean type still compiles unchanged.
4. Mark all transitive bindings stale. Audit CSSOM scrolling, sticky positioning, automatic minimum sizing, scroll timelines and viewport propagation as candidate consumers; their exact new behavior requires separate source reading. Do not infer it from the single changed rule.
5. Change the declarative semantics, then prove the executable normalization/refinement. Add the mixed-axis discriminator and unchanged controls. Require an independently reviewed allowed-observation relation for any permitted variability.
6. Review Gecko adapters separately: identify exact source predicates, phase and source revision, then obtain runtime evidence on the selected profile. Source applicability or an old-engine/new-draft disagreement alone is not proof of an engine defect.
7. Publish a migration report: changed, unaffected with evidence, stale, and unresolved. Ambiguous cross-module wording stays unresolved or becomes a CSSWG question with minimized competing traces. No silent selection of whichever interpretation matches a browser.

This exercise changes a shared semantic distinction. It tests whether the release system detects invalidated meaning, rather than merely accepting another successful compilation.

## 5. Interpretation and validation workflow

**Independent interpretation:** give the contract author prose, relevant definitions and host entry, without generated Lean or engine output. Require an explicit domain, temporal sequence, observations, exceptions and examples. Have a second reader challenge quantifiers and cross-family dependencies. Only then reconcile with the implementation-oriented model. Independence is organizational and semantic, not a claim that two generated files cannot share mistakes.

**Permitted variability:** specify allowed outcomes and persistent choice policies. Prove admissible choices exist; where consistency is required, quantify over one coherent history. A deterministic reference may implement one allowed policy. Engine conformance then checks membership in the relation, not equality to that arbitrary policy. Precision, resource failures and platform fonts require explicit contracts, not generic tolerances.

**Executable/reference validation:** preserve exact case identities, prerequisites and unsupported outcomes. Derive WPT assertions from reviewed observations; include spec links and assertion metadata, which WPT supports. [WPT CSS metadata](https://web-platform-tests.org/writing-tests/css-metadata.html). Differential runs across engines locate disagreements, not normative truth. Metamorphic transformations need their own side conditions: splitting text nodes, replacing units or reordering declarations is not universally semantics-preserving. Reduce failures without deleting the prerequisite that made them discriminating.

**Automation:** fetch and hash documents, discover links/definitions/grammar, propose requirement splits, detect changed bindings, generate routine proof scaffolding and search for witnesses. Webref distinguishes raw extracts from curated data with narrower consistency guarantees; it does not certify complete prose semantics. [Webref](https://github.com/w3c/webref). Bikeshed's algorithm markup aids structured discovery, not semantic proof. [Bikeshed](https://speced.github.io/bikeshed/#algorithms). Automated prose-to-Lean output remains a draft requiring interpretation review. Human/spec-editor judgment remains necessary for scope, exceptions, conflicts, interoperability constraints and policy choices.

## 6. Pilot sequence, exits and resource decisions

| Milestone | Measurable exit | Critical dependency |
|---|---|---|
| Portable release skeleton | A fresh source-only consumer checks exact claims/axioms; stale-interface and missing-observer packages are rejected | Toolchain/dependency and claim format |
| One existing vertical slice | One reviewed requirement reaches model, executable and one bounded source adapter with all premises classified | Independent prose contract and caller readiness |
| Overflow interaction pilot | Hidden/clip history and mixed-axis profile discriminator; complete admitted reference proofs; all semantic challenge failures explained | Box/axis/host observation interfaces |
| Hard-provider pilot | One sizing/fragmentation or text/font interaction with coherent provider histories and a useful nontrivial domain | Provider ownership, choices, numeric model |
| Spec-change rehearsal | Both profiles replay; affected claims become stale; reviewed migration restores only justified claims | Dependency graph and semantic interface ownership |
| External handoff | A reviewer outside the producing pair reconstructs one end-to-end claim and rejects a concealed assumption/observer mutation | Independent review capacity and reproducible package |

Only expand after these exits expose actual work. Record effort separately for interpretation, models, proofs, provider/source admission, integration and review; record rework after interface/spec changes and unresolved decisions. Estimate subsequent packages by comparable completed slices, dependency fan-out and provider novelty, with ranges and explicit assumptions. Do not extrapolate from theorem counts or invent a finish date.

Parallelize independent prose interpretation, proof production and adapter/test investigation. Keep one interface owner and one independent claim reviewer; rotate roles to avoid one shared interpretation becoming unquestioned. Limit active work to review capacity. Prioritize contracts reused across families and small falsifiable interactions before low-risk bulk property enumeration. A review queue, repeated adapter rewrites or unresolved semantic choices are signals to stop expanding producers and repair the interface.

## 7. Completion boundary

This report supplies a research plan and bounded critique, not accepted CSS semantics. Whole-CSS claims still require independently established normative coverage, host/role and observation completeness, cross-family composition, coherent permitted choices, and discharged or explicitly conditional providers. Engine coverage adds source, representation, scheduler, numeric/compiler, resource and lifetime obligations. None is replaced by the inventory prototype, a pure provider substitution theorem, WPT agreement or this report's integrity seal.
