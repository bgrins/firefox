# Whole-CSS feasibility: second research pass

19 October 2026. Three independent tracks extend the
[first roadmap](../css-whole-spec-roadmap-research-v1/README.md). These are reviewed
research proposals, not additional specification coverage or compiled proofs.
The complete selected CSS universe remains the objective.

## Results

| Track | Concrete contribution |
| --- | --- |
| [Inventory](inventory/REPORT.md) | A requirement-ledger schema, omission audits, and 19 worked records linked to existing fragments or explicit gaps |
| [Architecture](architecture/REPORT.md) | Three interface sketches, a dependency graph, composition theorem shapes, and a table separating external inputs from CSS behavior that still needs modeling |
| [Validation and delivery](validation/REPORT.md) | Acceptance gates, parallel work packages, an estimation method, and a historical CSSOM spec-change exercise |

Root read all three reports and authenticated their handoffs. Their individual
integrity checks pass; [ROOT-REVIEW.json](ROOT-REVIEW.json) records identities.
Integrity checks establish which research was reviewed, not that its conclusions
are formally proved. The worked inventory deliberately certifies none of its
19 requirements as closed: related proved fragments still have interpretation,
version and composition obligations.

## Changes to the plan

1. **Inventory before percentages.** Build a source lock and reconcile the full
   module catalog, then classify normative source units and dependencies. Keep
   historical versions distinct. The 19-record custom-property/CSSOM sample is
   a starting point for this machinery, not the denominator for all CSS.
2. **Layout and fragmentation need a shared protocol.** Box construction feeds
   layout, which creates fragments while processing lines, pages and columns.
   A fixed sequence that creates all fragments before layout is insufficient.
3. **External services cannot hide missing CSS.** Font bytes and device facts
   can be inputs; CSS font matching, percentage bases, query evaluation and
   resource-dependent updates still need explicit semantics and producers.
4. **Prove observable update behavior.** Incremental and fresh computations
   should agree on specified observations under the same environment and
   policy. Requiring all internal state to remain identical would conflate
   cache representation with CSS behavior.
5. **Measure effort with representative complete examples.** Sample parsing,
   style computation, layout and temporal behavior, including independent
   review and rework. The present research supports no defensible completion
   date or whole-CSS coverage percentage.

## Next implementation sequence

- Implement the source-lock and ledger validator; reject stale sources, missing
  dependencies, silent supersession and dangling proof links.
- Bind the sample requirements to exact source spans and theorem statements.
  Complete one custom-property-to-CSSOM observation path, including invalid
  versus valid-empty values, unique names, length and indexed access.
- Establish shared property-stage and environment-dependency interfaces with
  two actual clients. Continue the first roadmap's small property pilot.
- Extend that contract through ordinary box construction and one normal-flow
  sizing case with a parent or viewport mutation. Include provenance and
  dependency counterexamples before scaling into text and other layout modes.
- Demonstrate a real semantic spec update while preserving both old and new
  profiles. Then expand independent families against reviewed shared contracts.

Current bug-finding work provides a useful first composition target: the
custom-property map's nearest-owner lookup, iteration and stored count can
disagree. Correcting only iteration exposes the count defect. The ongoing native
and Lean work must join those contracts before claiming CSSOM enumeration
correctness. Its browser evidence and acceptance remain in separate artifacts.

The standalone semantics library, executable reference and Gecko refinement
retain separate claims. Even complete Stylo refinement would leave Firefox's
layout, text, painting and host behavior to connect before an all-CSS browser
conformance claim.
