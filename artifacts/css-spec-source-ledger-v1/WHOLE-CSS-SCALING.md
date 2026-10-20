# Expanding source accounting to a whole-CSS program

## Define the denominator before claiming coverage

Use a named, immutable profile: the dated [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/) as the stable catalog, plus an explicitly selected revision of each additional draft. The Snapshot distinguishes stability from browser adoption and identifies partial replacements of CSS2. A higher module level must therefore carry a reviewed replacement map and retained residual sections; dropping an entire older document is unsafe.

Maintain three separate denominators:

1. **Source accounting:** bytes and lexical units of the selected source files. This pilot accounts for 2,029,554 bytes, not three complete modules' semantics. The HTML source is only one multipage document.
2. **Interpretation coverage:** independently reviewed obligations for a declared conformance role and observable behavior, including guards, exceptions, permitted choices and progress. Splitting one obligation into ten records must not improve a coverage claim. Report unresolved source regions and requirement kinds alongside any counts.
3. **Assurance coverage:** those obligations discharged at the stated model, executable-reference or native-adapter tier, with transitive assumptions and provider obligations visible. A source link or a theorem over supplied inputs is not a native discharge.

The universe includes applicable inherited CSS2 requirements, modules/levels and errata, host-language integration, CSSOM observers, resource/font/Unicode providers, and dynamic histories. Boundary contracts can delimit a useful initial release, but an unresolved host obligation stays in the whole-CSS denominator. Normative references are candidates for dependency closure; hyperlink traversal alone is insufficient. The acquired [HTML style-block section](https://html.spec.whatwg.org/multipage/semantics.html#update-a-style-block) already exposes the need to include triggers and surrounding element state, not just a CSS algorithm name.

## What the implementation pilot changed in the plan

The v4 proposal's source-accounting gate now has a working implementation and an independent section check. Three practical constraints are no longer hypothetical:

- **A source anchor is not a complete contract.** The fragmentation target's 174 units preserve the four rule bodies and later fallback prose, but the adjacent `best-breaks` obligation still needs a manually recorded dependency. The independent reader proposed thirteen requirement candidates; that number has not become an accepted semantic denominator.
- **Validated references can contradict visible text.** Rule 4's class B text links to the class A anchor. Both are retained. Generating Lean from either alone could give a consistent but incorrect interpretation. Quarantine the ambiguous clause and retain competing interpretations until expert disposition; do not block unrelated source accounting.
- **Revision identity and requirement identity need separate layers.** This importer's document-qualified unit IDs all change after one source edit. That conservative invalidation is useful now. At scale, reviewed requirement IDs should remain stable while their source bindings change; similarity matching may propose mappings but cannot approve semantic continuity.

The importer accounts for lexical callbacks and explicit gaps, not an HTML5 DOM. Its current labels cannot determine nested normative context, image semantics or informative scope. This is a concrete limit on automatic extraction, not work to hide behind an “imported” status.

## Expansion gates and parallel work

| Gate | Measurable exit | Work that can proceed in parallel |
|---|---|---|
| Three-section accounting | Locked files, exact byte reconstruction, relocated replay, corrupt inputs rejected, independent section boundaries | Source acquisition and importer review |
| Three-section interpretation | Two independent clause readings reconciled; adjacent/incoming obligations reviewed; ambiguities and provider contracts assigned explicit statuses | Fragmentation, style-block and cluster specialists |
| First semantic integration | Nonempty examples and adversarial counterexamples; reviewed guards/observations; abstract proofs and an independently checked executable relation | Lean implementation, reference implementation and test-oracle review |
| Cross-family pilot | Style/resource change through font selection and layout/fragmentation with named temporal assumptions; no reset-to-fresh-state shortcut | Individual provider components once interfaces are reviewed |
| Catalog expansion | Every selected document/section has a disposition; replacement residuals and host frontiers accounted for; importer works on another document shape without silent drops | More module interpreters and source import workers |
| Release | Reproducible package, exact source/profile revision, tier-specific claim list, independently reviewed assumption closure, change invalidation and counterexample ledger | Mechanical replay and packaging after semantic review |

The first cross-family pilot should fail acceptance if a proof ignores the timing of a font/resource update while assuming fixed metrics, even when each local theorem passes. It should also fail if fragmentation permissions are replaced by one optimal layout without a proof that the selected layout is permitted. Missing interactions require an explicit frontier, not an inflated local theorem count.

## Automation and review capacity

Automate locked acquisition, byte/anchor inventory, syntactic candidates, source diffs, stale dependency invalidation, theorem inventories, kernel replay and test execution. Models may propose clause splits, Lean definitions and distinguishing examples. Human interpretation review must decide conformance roles, normative scope, permitted variability, replacement semantics, observer completeness and whether an assumption transfers across a caller. Independent proofs sharing a wrong classifier do not resolve that decision.

Allocate independent interpreters before implementation, then separate reference/oracle and proof/native reviewers. Batch mechanical work across documents; reserve scarce expert review for ambiguities, boundary contracts and interaction changes. Measure actual review/rework per accepted requirement kind and interface change, including rejected or reopened work. Use those observations to size later batches; no completion date or percentage follows from document bytes, tests or theorem totals.

## A concrete revision exercise

The retained exercise edits fragmentation's progress obligation from `must` to `may`. The old source lock and old ledger both reject the change. A new lock permits accounting, but cannot carry forward a universal progress theorem: interpretation review must decide whether progress remains required elsewhere, update the dependency ledger and adjust the admissible-behavior relation. The independent reference, counterexample expectations and Gecko-adapter claim then need separate review. A still-true theorem about the old stronger model does not establish correspondence to the changed specification.

This is a synthetic edit with exact receipts, not a claim that CSSWG made that revision. The independently reported CR/ED decoration-truncation difference is a separate real-version comparison outside this capsule's acquired source set. Both exercises illustrate why source accounting can scale mechanically while semantic acceptance cannot be inferred from it.
