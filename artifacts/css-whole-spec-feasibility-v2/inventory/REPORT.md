# Inventory and completeness: executable accounting plan

Research checkpoint, 19 October 2026. Builds on the prior whole-spec inventory, copied as `local/prior-inventory.md`. This package adds a concrete schema, a 19-record worked ledger and omission-audit rules. It does not claim an exhaustive CSS inventory or fresh proof acceptance.

## 1. Keep the entire objective; make versions explicit

Use **AllCSS@2026-10-19** as a versioned collection of specifications and requirements, not as a single union of inconsistent historical rules. Its master catalog includes:

1. Every module identified by the CSSWG draft catalog and current-work index, all Snapshot 2026 tiers, and the applicable remaining CSS2 clauses.
2. CSS-facing specifications maintained in adjacent repositories: CSSOM/View, Houdini registration/Typed OM/worklets, FXTF graphics, Web Animations and their CSS integrations. Repository location is not the inclusion criterion.
3. Print, speech, specialized media, device-dependent behavior and conformance obligations for style sheets/renderers/authoring tools. Low browser usage does not remove these from the objective.
4. Superseded, abandoned and legacy material in a historical branch with explicit status. It is accounted for rather than silently incorporated into the current semantics or discarded.
5. The invoked normative contracts of external standards. A reference to DOM does not require proving all DOM, but every tree/lifecycle operation actually used by CSS must have a tracked contract.

Discovery roots are the [CSSWG catalog](https://drafts.csswg.org/), [current-work index](https://www.w3.org/Style/CSS/current-work) and [dated Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/). The catalog contains early drafts beyond the stable snapshot. [browser-specs](https://github.com/w3c/browser-specs) and [Webref](https://github.com/w3c/webref) provide useful secondary machine-readable discovery, not an exhaustive normative denominator.

For each document select exact rendered bytes, source repository revision where available, publication/status/date, and dependency versions. Do not let a mutable `/TR/shortname/` or editor URL silently change a proof target. Maintain two coherent views over the master inventory: the dated snapshot baseline and the reviewed current-draft composition. Those are organizational views, not a retreat from the complete objective. Later spec changes create a new view and explicit transfer obligations.

**Supersession is clause-level.** For example, Snapshot 2026 says Box Model 3 replaces specified CSS2 sections but excludes margin collapsing in §8.3.1. Values 5 explicitly describes itself as a diff against Values 4. Selecting only the highest level loses inherited requirements. Represent `replaces`, `extends`, `amends`, `imports-contract`, `conflicts-with` and `editorial-move` edges. Unresolved conflicts block that combined view; they do not license choosing whichever behavior is easiest to prove. [Snapshot module interactions](https://www.w3.org/TR/css-2026/#css), [Values 5 introduction](https://drafts.csswg.org/css-values-5/#intro).

The catalog reconciliation itself is unfinished here. Full source locks and complete inventories must be produced by the first implementation task below; this report is not a claimed complete AllCSS roster.

## 2. Files to implement

| File | Required content / invariant |
| --- | --- |
| `spec-lock.json` | Canonical document and revision IDs, complete bytes/source hashes, date/status, repository, retrieval identity, conformance classes and selected views |
| `source-units.jsonl` | Every source paragraph, list branch, grammar production, definition-table cell, equation, normative figure and advisement; stable DOM/source locator plus hash; explicit informative classification |
| `requirements.jsonl` | Stable semantic ID, immutable revision, normative source-unit IDs, quantifiers, conditions, input/output/error/temporal obligations, permitted choices and interpretation review |
| `dependency-edges.jsonl` | Requirement-level imports, supersession, generic-rule instantiations and cross-module interaction edges; exact versions and unresolved edges |
| `coverage-links.jsonl` | Many-to-many links to Lean definitions/theorems with exact declarations, hashes, proof replay and the subset of the requirement actually covered |
| `premises.jsonl` | Provider/codec/host/math/device/compiler/heap assumptions; owner and disposition for discharge or declared external contract |
| `open-interpretations.jsonl` | Normative ambiguities, contradictions, intentionally unspecified behavior, unresolved CSSWG issues and retained counterexamples |
| `inventory-audit.json` | Source coverage gaps, duplicate/missing records, unresolved references, independent review and changed-source invalidation |

Use IDs such as `CSSREQ-CUSTOM-INVALID-VS-EMPTY`, not section numbers as identity. A new semantic interpretation creates a new revision; split requirements retain explicit `split-from` links. URLs/anchors locate the text, while source hashes prevent an anchor from silently changing meaning. Generic rules are quantified over property registries; their reviewed instantiations link every property/descriptor that uses them. Do not enumerate infinitely many custom-property names or all numeric values.

Classify obligations before formalization:

- **Grammar:** productions, lexical conventions, global CSS-wide additions, ranges and recovery. Parsing success alone does not establish computed or rendered behavior.
- **Algorithms and relations:** branches, state updates, ordering, error exits and observables, including prose without a MUST keyword.
- **Definition tables:** applicability, initial/inherited/computed values, animation type and percentage basis become distinct obligations.
- **Conformance:** style-sheet/renderer/authoring-tool classes, unsupported-feature handling, security/privacy requirements and allowed resource limits.
- **Choices:** underspecified ordering, device capability and language-sensitive behavior become constrained relations or parameters. An arbitrary oracle must not erase the constraints.
- **Temporal composition:** loading, mutation, event/promise order, style/layout feedback and published observations.

The specification's own conventions determine what is normative. For example, Values 4 distinguishes informative examples/notes/tests from normative advisements, and explicitly separates conformance classes. [Values 4 conformance](https://drafts.csswg.org/css-values-4/#conformance).

## 3. Worked ledger slice

`ledger-slice.json` contains 19 stable-ID records, source links, dependencies, local coverage feature IDs and explicit gaps. This is a cross-version demonstration, not one already reconciled conformance view. The selected coverage records and six relevant Lean source modules are copied under `local/`; their hashes are retained. No Lean compilation was performed for this research.

| Stable ID suffix | Requirement and source | Existing evidence / remaining admission |
| --- | --- | --- |
| `CUSTOM-NAME-IDENTITY` | Exact custom-name identity. [Variables 1](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#defining-variables) | `named-custom-declaration-cascade`; already-normalized names, not full host/source decoding |
| `CUSTOM-VAR-GRAMMAR` | Absent versus empty fallback. [Variables 1](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#using-variables) | `closed-raw-values`; bounded grammar, not arbitrary component values |
| `CUSTOM-INVALID-VS-EMPTY` | Invalid and valid-empty values differ. [Variables 1](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#guaranteed-invalid) | Normalized Option semantics; serialization/source join open |
| `CUSTOM-CYCLE-EDGES-SNAPSHOT` | Static references include fallbacks. [2022 cycles](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles) | `VariableExpr.references_iff`; selected binding/source construction required |
| `CUSTOM-CYCLE-INVALIDATION-SNAPSHOT` | Cycle participants become invalid. [2022 cycles](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles) | `VariableBindings.cyclicBool_iff`, recursive solver; source and full domains remain conditional |
| `CUSTOM-INHERIT-COMPUTED` | Child receives computed inherited values. [Variables 1](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/#cycles) | `VariableEnvironment.missing_inherits`; forest/host admission separate |
| `CUSTOM-VAR-REPLACE-DRAFT` | Current var replacement. [Variables 2](https://drafts.csswg.org/css-variables-2/#using-variables) | Fresh-root var-only profile; general functions and taint absent |
| `SUBSTITUTION-CONTEXT-GUARDS-DRAFT` | Guarded context/cycle propagation. [Values 5](https://drafts.csswg.org/css-values-5/#arbitrary-substitution) | `GuardedSolver.compute_iff`; context universe and cache composition incomplete |
| `DECLARATION-HEADER-RECOVERY` | Identifier/colon failure recovery. [Syntax 3](https://drafts.csswg.org/css-syntax-3/#consume-declaration) | `declaration-consumption-boundary`; full contextual validity separate |
| `DECLARATION-IMPORTANT` | Terminal important processing. [Syntax 3](https://drafts.csswg.org/css-syntax-3/#consume-declaration) | Related structural layer; exact per-theorem mapping still needed |
| `DECLARATION-CUSTOM-ORIGINAL-TEXT` | Preserve custom-value source text. [Syntax 3](https://drafts.csswg.org/css-syntax-3/#consume-declaration) | Source-dependent completion differs from decoded value; whole CSSOM bridge unestablished |
| `CSSOM-COMPUTED-APPLICABILITY` | Host and pseudo conditions. [CSSOM](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) | No complete host gate mapped |
| `CSSOM-CUSTOM-MEMBERSHIP` | Include non-invalid computed custom properties. [CSSOM](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) | Native iterator work is not complete computed-map/host refinement |
| `CSSOM-CUSTOM-ORDER` | Custom order currently unspecified. [CSSOM](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) | Choice record; preserve membership and coherent indexing |
| `CSSOM-DECLARATION-LENGTH` | Declaration count. [CSSOM](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-length) | Uniqueness does not prove correct stored length |
| `CSSOM-DECLARATION-ITEM` | Indexed name or empty string. [CSSOM](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-item) | Count, FFI/WebIDL and list-coherence bridges open |
| `CSSOM-COMPUTED-LIVE` | Live computed readonly object. [CSSOM](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) | Static models do not cover update/publication histories |
| `MATH-RESOURCE-LOWER-BOUND` | Minimum supported capacities plus invalid excess. [Values 4](https://drafts.csswg.org/css-values-4/#calc-syntax) | Resource parameter/recovery obligations, not unlimited mathematical evaluation |
| `PARTIAL-SUPPORT-ATOMIC-INVALIDITY` | Unsupported components invalidate the declaration. [Values 4](https://drafts.csswg.org/css-values-4/#partial) | A complete support classifier is not provided by bounded property profiles |

The 2022 static-cycle records and the current guarded records deliberately remain distinct. Existing `GuardedExamples.snapshot_draft_difference` records a model disagreement. A theorem for one version cannot silently satisfy the other's obligation. Current CSSOM itself imports its guaranteed-invalid definition from Variables 2, illustrating why a document name alone is an insufficient dependency pin.

All 19 rows have `certified_closed: false`: this research has not audited the complete source-to-model interpretation, provider discharge and revision correspondence. That does **not** mean the existing theorem statements are unproved. It means a related checked fragment is not yet a certified whole normative requirement.

## 4. How to detect omissions

An omission audit must work in both directions.

1. **Corpus reconciliation:** compare Snapshot, CSSWG catalog/repository metadata, adjacent groups and Webref/browser-specs inventories. Every extra/missing document gets an explicit disposition. Follow both normative references and normative prose links; bibliographies alone miss implicit dependency contracts.
2. **Source partition:** assign every source unit to a requirement, an explicitly informative classification, a superseded clause or an interpretation issue. Zero unclassified units is an inventory milestone, not semantic correctness. Preserve overlapping and inherited requirements explicitly rather than double-counting.
3. **Structural cross-checks:** reconcile all property/descriptor table cells, grammar productions, at-rules, functions, IDL members, algorithm branches, equations and normative figures. Verify inherited global syntax/behavior for every applicable registry entry.
4. **Dependency closure:** unresolved local targets and imported contracts fail the audit. Generic proof instantiation must cover the entire declared registry. Track feedback edges such as layout→container queries rather than assuming a one-way pipeline.
5. **Independent interpretation pass:** a second reviewer classifies source without seeing proposed coverage, then compares omissions and disputed granularity. The proof producer should not solely define the denominator their work is judged against.
6. **Reverse proof check:** every credited theorem must expose its domain, premises, observable relation and exact requirement revision. Flag assumed target behavior, weakened domains, stale source, vacuous premises and counterexamples.
7. **Observation challenge:** WPT inventories, fresh differential probes and semantic mutants challenge interpretation and implementation; they cannot certify universal completeness. No metadata file is not evidence that a test was executed.
8. **Spec-change gate:** source changes invalidate affected records and transitive dependency consumers until reviewed. Editorial moves preserve semantic IDs; substantive changes require revised obligations and transfer proofs.

Important residual: complete source-unit classification still cannot mechanically prove that every implication of prose was interpreted correctly. Independent standards review and targeted counterexamples remain part of the trusted interpretation process.

## 5. An honest completion dashboard

Keep separate reports for:

- catalog/source classification: documents and source units resolved versus unclassified;
- requirements: interpreted, modeled, proved under named premises, premise-closed, ambiguous, refuted and not yet modeled, grouped by family/version/kind;
- dependency obligations: unresolved imports, host/provider contracts and cross-family joins;
- native refinement: exact implementation revision, source admissions, implementation invariants and observations;
- maintenance: stale revisions, unreviewed spec deltas and broken transfers.

A count is meaningful only against a frozen, independently reviewed ledger with stable granularity. Do not combine theorem, requirement, property and fixture counts into a percentage. Even a requirement-count ratio would measure accounting progress, not equal-weight semantic difficulty; label it accordingly and preserve split/merge history. Report complete named families and remaining critical dependencies instead of an overall CSS percentage.

For a specific coherent version view, semantic completion means every applicable normative requirement has a reviewed formal relation and proved coverage, including errors, temporal behavior and permitted choices. Any external contract in the final claim must be enumerated. Remaining unresolved ambiguities or false premises prevent an unconditional completeness claim. Entire-CSS completion additionally requires every current module and all applicable media/classes in the master objective, not only a desktop subset. Historical conflicts remain separately versioned theories.

## 6. Practical next implementation tasks

1. Implement source-lock acquisition and catalog reconciliation, storing complete rendered/source bytes and revisions. Produce the first explicit AllCSS document roster and exceptions report. Research excerpts here are insufficient as the production source lock.
2. Implement the ledger schema and validator. Reject duplicate IDs/revisions, unclassified source units, unknown dependencies, dangling proof links, silent supersession and stale hashes.
3. Turn this 19-record sample into a fully bound pilot: complete exact source spans, independently split compound rows where necessary, import declared external contracts and review exact Lean statements. Finish one custom-property-to-CSSOM observation path without declaring Variables or CSSOM wholly covered.
4. Apply the same process to one layout module and one font/rendering module. This tests whether the schema handles equations, geometric choices, algorithm iteration, device limits and cross-module used values rather than only text algorithms.
5. Migrate the existing 127 historical coverage features through many-to-many links. Preserve their exclusions, version differences and conditional admissions. Do not turn `checked_fragment` into `certified_closed` automatically.
6. Add change detection and independent omission review before scaling agent production. More generated proofs without a reviewed denominator can increase confidence in the wrong scope.

No calendar estimate follows from this sample. Main unknowns are the size and granularity of the reconciled requirement set, unresolved standards issues and the effort to connect fonts/layout/host services. These are measurable research tasks, not reasons to narrow away the full objective.

## Evidence boundary

Primary web retrievals with tool/crawl metadata are retained under `sources/`; they are rendered excerpts, not complete raw HTML. The JSON's source bindings are expressly provisional until full acquisition. Local coverage and six Lean modules were read/copied, not executed. No native, browser, Git or production changes were made. The map proof checkpoint remains separate and unsealed.
