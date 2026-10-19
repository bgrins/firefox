# Roadmap toward a comprehensive CSS model in Lean

Research synthesis, 19 October 2026. This is a proposed direction, not a claim of
new specification coverage or a migration of the existing library. Work stays
local; no publication or external submission was performed.

## Assessment

A comprehensive, versioned formal CSS semantics is a plausible long-term research
objective. The present project is a useful foundation for syntax, selectors,
cascade and selected values. It does not yet model most layout, text/font,
rendering, animation or dynamic host behavior. More Lean declarations alone will
not close those gaps: the main work is choosing faithful semantics, designing
shared interfaces and proving that their contracts compose.

The whole-CSS objective remains the complete selected specification universe.
Smaller named profiles are intermediate milestones, not a replacement objective.
An excluded module remains visible in the global backlog, even when a narrower
profile can be released as complete.

## Three complementary reviews

- [Specification inventory and dependencies](spec-inventory.md): scope policy,
  clause supersession, thirteen-family gap map and staged exit conditions.
- [Architecture](architecture.md): implementation strategy, shared semantic
  interfaces, package boundaries and three concrete implementation pilots.
- [Validation and evolution](validation-and-evolution.md): interpretation review,
  completion criteria, safe automation, version updates and standalone governance.

The inventory starts from the dated [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/),
then explicitly selects and pins newer drafts and CSS-adjacent dependencies.
Snapshot stability categories are not browser-adoption categories. Higher module
levels can replace only parts of older definitions; a blanket union or highest-
level-only selection is insufficient. Printing, speech, UA latitude and optional
behavior need an explicit disposition rather than disappearing from “all CSS.”

## What complete would mean

| Dimension | Required closure |
| --- | --- |
| Inventory | Every applicable normative requirement, replacement and dependency accounted for at exact revisions |
| Semantic model | Reviewed definitions represent all in-profile behavior, errors, permitted choices and interactions |
| Executable reference | Algorithms terminate/progress where required and are proved sound and complete against independent relations |
| Implementation refinement | A particular engine's representations, algorithms, callers and effects agree with the model over the advertised domain |

Tests, model theorem counts and source-binding hashes are separate evidence.
None proves faithful translation of English by itself. The current library's
127 feature records are overlapping historical fragments, not a percentage of
all CSS. Stylo refinement would also leave Gecko layout, text/font and painting
components to verify before claiming all-CSS browser conformance.

## Proposed sequence

1. **Make the requirement ledger real.** Pin the module/version universe and
   replacement graph, then map existing coverage records to stable requirement
   IDs. Pilot on selector matching, cascade/defaulting and substitution. Track
   interpretation, definitions, proofs, tests and native admissions separately.
2. **Establish shared contracts.** Agree on syntax/source identity, property
   stages, host subjects, environments, geometry, time and observable histories.
   Preserve existing accepted modules behind explicit adapters; avoid a blanket
   rewrite or silent merging of incompatible profiles.
3. **Close a complete style-computation slice.** Extend the current source-to-
   computed-value foundation with reviewed property dispatch and mutation
   semantics. Prove actual entry/exit composition, including unsupported versus
   invalid input, rather than assuming the internal entry state is ready.
4. **Build the layout foundation.** Model box construction, writing modes,
   containing blocks, sizing and ordinary flow. Join text/font metrics and break
   opportunities through precise contracts. Distinguish DOM nodes, boxes and
   fragments; one identity type cannot faithfully represent all three.
5. **Expand independent families.** Flex/grid/tables/fragmentation, text/fonts,
   painting/colors/transforms, animation and condition evaluation can proceed
   in parallel once shared interfaces are stable. Their composition obligations
   remain part of the work, not a final testing exercise.
6. **Close host and temporal behavior.** Join resource loading, CSSOM mutations,
   queries, font changes, animation effects and incremental recomputation to
   observable values, geometry and event histories. Model specified feedback and
   cycle breaking explicitly, rather than postulating a generic fixed point.
7. **Audit a pinned whole-profile release.** Require every in-profile requirement
   and dependency to be discharged or honestly exposed as a genuine external
   contract. Keep unresolved interpretations and the wider whole-CSS backlog
   visible. Reproduce old and new profiles across a real semantic spec change.

## Recommended first implementation

Start with the requirement ledger and architecture Pilot A together. Use
`visibility`, `opacity`, and a documented length/percentage profile of `width`
to exercise inherited/reset properties, numeric computation, percentage bases,
used-value requests and resolved-value observations. Preserve existing proofs
through embeddings rather than changing their premises silently.

The deliverable is a shared property-stage and environment-dependency interface,
used by at least two existing clients, plus a theorem connecting a delivered
parent/environment update to fresh computation. A stale-dependency mutant must
fail. Invalid, pending, unsupported and successful outcomes remain distinct.
This is an interface milestone toward whole CSS, not a claim to implement all of
those properties or all native scheduling.

After that interface is reviewed, run box-provenance/ordinary-layout Pilot B and
actual-animation-value Pilot C in parallel. The latter can reuse the already
accepted conditional animation identity result after an explicit mapping into
the common property registry. Text/font and painting interface work can proceed
alongside them, with real consumers required before claiming composition.

## Project shape and safeguards

Keep implementation-independent semantics, a proved executable reference,
validation/traceability tooling and Gecko adapters separately versioned. Other
engines should be able to use the semantic library without Firefox. External
researchers should be able to replay a small module without building Gecko.

Use Bikeshed/Webref to discover terms, grammar tables, references and changes.
They do not extract all normative meaning. Agents can draft models and proofs,
build adapters, search for counterexamples and maintain mappings; independent
semantic review remains necessary. Ambiguous prose needs recorded alternatives
and, where useful, a draft CSSWG issue rather than an invented definitive answer.

Assumptions must have owners at each layer. A local helper's frame theorem must
not silently become a whole-engine history theorem: our substituted-inherit
review demonstrates that fresh-style construction can recompute unrelated flags
even though the selected helper preserves its incoming flags. Similarly, an
abstract font provider does not discharge all required font selection/loading
behavior. Report the exact remaining contract and the component that must prove it.

## Planning limits

No defensible all-CSS percentage or completion date follows from current line,
theorem or test counts. This research has not enumerated every normative clause.
The next measurable milestone is a versioned requirement graph and one connected
implementation pilot with reviewed interfaces, an endpoint theorem, explicit
assumptions and discriminating tests. Existing bug finding and standalone native
fix commits continue independently while this architecture is developed.
