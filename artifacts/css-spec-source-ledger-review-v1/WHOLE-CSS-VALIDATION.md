# Establishing faithful coverage of all CSS

The final objective remains all CSS under a named evolving normative profile. Partial family pilots are milestones, not a redefinition of that objective. The v4 inventory/validation architecture remains appropriate; the source importer now supplies a concrete piece of its acquisition/accounting layer. It has not supplied a semantic completeness certificate.

## Three claims with different acceptance gates

| Claim | Evidence needed | What this pilot actually establishes |
|---|---|---|
| Faithful specification model | Independently reconciled requirements, exceptions, choices, observations and external contracts; inhabited domains; reviewed statements | Proposed fragmentation interpretation and exact source boundaries |
| Correct executable reference | Refinement to that model; permitted outcomes, errors, progress and numeric/provider contracts | No executable fragmentation algorithm yet |
| Native conformance | Exact engine/source/data profile; representations, caller admission, arithmetic, scheduling and observers connected to the model | No native claim in this pilot |

A proof checker establishes that a theorem follows from its definitions and assumptions. To determine whether those are the right definitions, use independent readers before either sees the other's interpretations, preserve disagreements, and require explicit disposition. Then adversarially remove an exception, weaken a guard, substitute the wrong observer or make the domain empty. An executable and theorem sharing the same mistaken interpretation can agree perfectly.

## What the actual fragmentation pilot catches

[Unforced breaks](https://drafts.csswg.org/css-break-3/#unforced-breaks) stressed the proposed pipeline in concrete ways:

- The lexical range is complete, yet four numbered rules alone omit the later fallback and progress clauses. Requirement coverage needs many-to-many source bindings, not one row per heading.
- The correct range ends before best-breaks; its adjacent zero-size placement obligation still belongs in the dependency frontier. Following explicit links cannot discover every obligation.
- A class B label links to class A. Resolving all links is weaker than interpreting the source consistently. Both tokens and disagreement must survive importing.
- The ED and published CR differ in decoration truncation. Revision selection and migration decisions matter before any theorem is generated.
- A permitted choice is not an exact expected cut. A strong-looking unique-output theorem can reject conforming implementations.
- Nonzero geometric progress is not automatically well-founded termination. A finite cursor pilot needs an explicit correspondence boundary before its proof can be generalized.

These are operational checks on the v4 plan: source-unit coverage, reviewed interpretation, nonvacuity and dependency closure remain separate gates. The current importer genuinely advances the first, while the independent candidates advance review preparation for the second.

## Omission detection and choice contracts

Maintain an independently reconciled module/version catalog, including residual older sections and host integration. Within each selected source, account for prose, algorithms, grammar, property tables, figures and inherited normative context. Within each requirement, inventory guards, normal outcomes, exceptions, failures, allowed choices and observations. Cross-check these three levels: missing documents are invisible to a clause table; missing exceptions are invisible to a byte partition; missing observers are invisible to a screenshot oracle.

For underspecified behavior, define a permitted relation plus nonemptiness/consistency obligations. An implementation may choose a policy only after proving its outputs remain in that relation. Persist choices across observations where the specification requires consistency. Do not grant an unconstrained provider merely because the prose permits more than one answer. Disagreements or apparent contradictions remain open interpretations rather than being silently resolved to match current Firefox.

## Fonts, host behavior and composition

External inputs need versioned contracts with explicit responsibility. Distinguish CSS-owned matching/selection rules from font support facts, Unicode data, platform fallback policy and shaping results. Supply nonempty supported and unsupported examples, missing-data outcomes and consistency across repeated requests. A theorem conditional on a correct provider is valuable, but it does not verify that provider.

HTML/SVG integration needs trigger and observation contracts: which tree/style/resource events update which object, when that update becomes observable, and what errors or absence mean. Styling, layout, font selection, animation and painting must agree on identities, phase and environment versions. A local proof about a supplied stable state cannot stand in for a proof that the host obtains that state after mutation. Shared-interface revisions must invalidate every dependent claim, including proofs whose Lean source still compiles.

## A defensible coverage report

Report separate, source-bound sets and open frontiers:

1. Acquired/reconciled catalog entries versus unresolved or excluded entries, with reasons.
2. Source units dispositioned versus unclassified units, separately from reviewed semantic requirements.
3. Reviewed requirements with model bindings, executable refinements and native bindings in separate columns.
4. Transitive assumptions, unresolved conflicts, unsupported domains and external providers per claim.
5. Independently reviewed observers, nonvacuity witnesses and mutation challenges, with remaining omissions.

Do not combine these into one percentage. Raw bytes, thirteen candidate requirements or a theorem total are not comparable measures of semantic difficulty or all-CSS coverage. A percentage is defensible only for a precisely named, independently reviewed denominator and one specific claim level; it must retain the unreviewed catalog frontier rather than implying global completeness.

## Next practical gate

Finish independent reconciliation of all three pilot sections. Bind a small reviewed requirement set to real Lean declarations and record the unresolved remainder. For fragmentation, first implement the finite relational choice pilot proposed in INTERPRETATION.md, with stage witnesses and explicit geometry/provider boundaries. Then perform a real source-revision migration: retain the old profile, review the changed clause/interface, invalidate dependencies and re-establish the affected contracts. Only after that composition exercise should broader family coverage be reported as more than source accounting.
