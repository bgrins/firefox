# Fixed-anchor v2 required interpreter and trace extension

2026-10-18. Proposed implementation boundary; v1 remains frozen. The successful v1 structural theorems, exact native bridge, mutations and independent raw-wire review remain valid bounded evidence, but do not satisfy the original universal interpreter-agreement milestone.

## Two independent Lean algorithms

1. A specification program represents an ordered candidate occurrence with its descendant program and remaining alternatives, explicit list/pass and placeholder events, and frame-call boundaries. Its interpreter chooses by the four candidate decisions. It does not call the native-shaped interpreter. Erasure to the existing `Plan` gives a bridge to its exclusion/safety/preservation lemmas; added annotations do not change selection.
2. The native-shaped interpreter directly implements `FindAnchorIn` over raw ordered child lists, skipping the three first-pass kinds, returning on success, then examining the absolute list. Its `FindAnchorInList` counterpart recursively examines raw slots, resolves placeholders, rejects external targets, classifies candidates, calls child-frame traversal only for PassThrough/Traverse, and applies their different fallbacks. It must not call `Plan`, its compiler, or its interpreter to obtain a result.

The theorem compares the complete outcome (selected candidate plus semantic trace), not only IDs. Induct over recursive descent fuel and arbitrary finite slot/list lengths. Quantification includes every graph observation and ordered list satisfying named provider premises; repeated occurrences and aliases are not deduplicated.

## Event schema and native mapping

| Event | Source observation |
| --- | --- |
| Frame entry/completion | `FindAnchorIn(aFrame)` call and actual returned candidate/null |
| First-pass list entry or skip | Actual ChildLists enumeration, parent ID, kind, and skip predicate |
| Absolute-pass entry | GetChildList(Absolute) after all first-pass lists failed |
| Slot/placeholder resolution | Raw slot ID, resolved target ID; proper-ancestor acceptance/rejection when target differs |
| Candidate decision | Actual `ExamineAnchorCandidate` return, stable candidate ID |
| Descend | PassThrough/Traverse call to `FindAnchorIn(child)` |
| Branch return | Accept return, successful child return or Traverse fallback return, with source and result IDs |
| Fallback | Traverse's child traversal returned null and the candidate itself wins |
| Final selection | Public traversal result, including maintenance-disabled null |

The existing C++ provider events remain distinct from this semantic trace. Do not label interpreter-generated annotations as direct C++ events.

For bounded source binding, generate a separate instrumented translation unit from the exact extracted functions using a fixed insertion inventory with unique-match and before/after body hashes. Insert trace writes at the named call/branch boundaries only. Ordinary original/candidate translation units remain verbatim and retain all v1 provider/state checks. Require instrumented builds to match ordinary selected values, flags, offsets, other public state and original provider traces on every input, then compare their separate semantic trace with both Lean algorithms and an independent raw-input oracle. Instrumentation is explicit derivative code, not the ordinary exact-body certificate.

## Rank and provider premises

Use the actual ordered provider graph, including resolved local placeholders and the second absolute pass. A nonnegative rank decreases across every recursive candidate-descendant edge. Physical-parent consistency, valid IDs, finite lists, stable styles/geometry/ancestry and absence of mutation during traversal remain bridge assumptions. Repeated sibling or absolute-pass visits are legal; cycles are rejected rather than deduplicated.

Prove fuel stability for the complete rich program/outcome once fuel exceeds the relevant frame rank, then state interpreter agreement for arbitrary finite ranked graphs. Universal fuel-parametric agreement alone is not presented as an unbounded traversal theorem. Rank proofs must account for valid aliases; invalid placeholders do not create descent edges.

## Required preservation and linkage

- Full no-fixed trace and selection preservation, including list/pass, resolution, classification, descent, returns and fallback.
- Rich specification interpreter erases to the existing structural selection semantics, or an explicitly proved equivalent structural safety theorem if representation changes make erasure unsuitable.
- Selected-node safety and conditional excluded-route barriers carry through the universal Lean interpreter agreement.
- Retain the alternate-route witness and public/flag/state bounded bridge. Highlight invalidation remains singleton-continuation provider coverage; no full continuation-chain theorem is added silently.
- Keep existing v1 tests and add traces that distinguish duplicate absolute visits, rejected aliases, empty PassThrough, Traverse fallback, nested returns and unchanged winners with different control flow.
- New semantic Lean mutations need successful changed-output counterexamples plus proof rejection. Native assertion-invalid controls stay outside full-corpus semantic counts.

## Limits and delivery

This is a universal **Lean interpreter-to-interpreter** refinement under named graph/provider premises plus bounded source-bound C++ execution. It is not universal C++ refinement, verified compiler output, memory safety or a proof of Gecko frame construction/geometry. No browser/native/WPT/shared-build/Git work belongs to this extension.

Publish the new model, extraction/instrumentation inventory, independently readable oracle, exact source/tool pins, source-only closure, full replay and mutation receipts in v2. Preserve v1 files and their rejected/successful preparation history. Root replay and independent review remain acceptance gates.
