# Whole-CSS Lean research: third pass

19 October 2026. Three complementary reviews extend the earlier roadmaps. Root
read all three reports, authenticated their handoffs and ran their integrity
checks. This is research and prototype bookkeeping, not new CSS proof coverage.

## Findings

| Track | New contribution |
| --- | --- |
| [Inventory](inventory/REPORT.md) | Separate catalog discovery, complete source accounting and coherent versioned normative views; ten cross-family ledger examples and an omission audit |
| [Semantics](semantics/REPORT.md) | Six integration stress tests, including sizing phases, reshaping, structural transforms, query/animation events and permitted sampling delays |
| [Validation](validation/REPORT.md) | Independent challenge contracts, premise dependency closure, a full taint observation trace and a display-animation/inertness migration exercise |

The inventory prototype rejects ten deliberately corrupted ledgers. Its ten
worked rows are proposed interpretations with unbound model/proof/engine fields;
they neither enumerate all CSS nor establish independently approved semantics.
The interface sketches are uncompiled proposals.

## Architecture decisions to carry forward

1. **Use versioned normative views.** A union of current drafts can contain
   conflicts and lose older rules that remain applicable. Record scoped
   supersession, residual clauses, role/medium guards and incoming host-standard
   integrations. Keep unresolved and experimental entries visible without
   silently making each one an active requirement.
2. **Model permitted choices across histories.** An engine can implement one
   permitted policy. The semantics must retain the alternatives and their
   consistency constraints. Arbitrary independent provider answers are too weak.
3. **Give requests phase and ownership.** Intrinsic sizing and used sizing can
   resolve the same percentage differently. Text layout can request reshaping.
   Identity transforms can change containing blocks even when their matrices do
   not move pixels. These effects need explicit interfaces and shared identities.
4. **Make observation timing part of the contract.** Scroll-driven animation
   rules can intentionally expose sampled state. Replace universal freshness
   with the specified sampling protocol and compatible provider epochs; this
   must still reject stale values where the specification grants no delay.
5. **Track assumptions transitively.** A release claim inherits every open
   provider, interpretation and native-adapter obligation in its dependency
   graph. More local theorems cannot close an omitted composition edge.

## Recommended implementation order

### 1. Build the catalog and requirement ledger

Implement source locks, scoped replacement/dependency edges, source-unit
accounting and stale-binding rejection. Independently classify representative
sections covering flex distribution, fragmentation permissions, HTML style-block
updates and our custom-property/CSSOM work. These exercise different semantics;
none becomes a substitute for the full inventory.

### 2. Close one existing observation path

Use the current custom-property work to join parsing/defaulting, computed values,
metadata-aware map updates, substitution, byte ranges and URL observations.
Keep native refinement separate from the specification relation. Include temporal
replacement so equal serialization cannot hide stale origin metadata. The recent
native repairs supply discriminating examples; their conditional proofs do not
yet close the entire path.

### 3. Test shared interfaces with difficult clients

Develop a phase-aware percentage-sizing case with two consumers, then a real
box/text/fragmentation boundary. Add an observation protocol that distinguishes
required fresh reads from prescribed sampled animation state. Require
nonvacuous executions, progress where specified and counterexamples to erased
phase, owner or epoch information before expanding a family.

### 4. Exercise semantic maintenance

Preserve two spec profiles through a real semantic change. The proposed display
exercise must update animation behavior and its separate HTML inertness
dependency; an interpolation-only update should fail the review gate. Measure
implementation, interpretation, integration, review and rework effort to inform
subsequent planning.

## Standalone artifact and completion claims

Keep specification profiles, semantics, executable reference, validation tooling
and engine adapters separately versioned. The semantics must be useful without
Gecko types or a Firefox build. Native adapters retain the source, representation,
provider and scheduling details necessary for engine conformance.

There remain three different endpoints: a comprehensive specification model,
a proved executable reference over its declared domain, and a particular engine
proved to conform. The first is a plausible sustained research program; the
others require additional work. None has a defensible completion percentage or
schedule from our present evidence. Whole-Firefox CSS conformance extends beyond
Stylo into layout, fonts, graphics, host APIs and scheduling.

Inventory and semantics retain primary source snapshots. Validation retains
web retrieval records rather than full immutable primary pages; its migration
exercise is a proposal requiring source locking before implementation acceptance.
The package checkers establish research identity and internal bookkeeping, not
faithful translation of prose or mathematical correctness of the sketches.
