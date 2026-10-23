# Independent compact landing-test review

**GO for testing the proposed partition. HOLD native acceptance until these exact compact files run and outstanding boundary results are adjudicated.** No source blocker was found in the selected assertions or registration changes. This review ran no browser, compiler, build, or Git mutation.

Authenticated proposal FILES: `452f970358ea356592a42c9db01dd38e31274eb8833564a41516f43d7fbc604c`. All eleven payloads and four source-fixture pins match. `CHECKS.json` records each file hash, independently reconstructed names and exact callback comparisons.

## Partition and preserved mechanisms

| Repair | Tests | Retained distinction |
| --- | ---: | --- |
| Principal: measurement | 12 | Direct item versus descendant; shrinking versus no-shrink/zero sibling; visible/hidden; insertion and removal |
| Principal: fixed size | 8 | Flex versus block; initially visible/hidden; bounding rectangle versus offset dimensions |
| Principal: placement | 18 | Item/leaf append and prepend; all four parent-style changes under one/two hidden ancestors; anonymous text Range append/prepend |
| Absolute: direct geometry | 4 | Static/explicit positions; visible/hidden; insertion and alignment change |
| Absolute: descendant geometry | 8 | Leaf queried before OOF parent; static/explicit offsets; append/prepend; one/two hidden ancestors; parent resizing |

Totals independently reconstruct to **38 principal + 12 absolute**. All132 original diagnostic names are accounted for exactly once:50 selected,82 retained only in the larger diagnostic corpus. All selected registration names map back to their original identities. The six callback templates in the four edited files retain their exact original bodies and registration templates; only outer selection and unused helpers/styles change. The eight-test OOF leaf file is byte-identical to its diagnostic source.

The preexisting sizing-route identities `Flex item, hidden, append, shrink, bounding` and `Descendant, hidden, append, shrink, bounding` remain. This matters because fixed-size exposure alone would not demonstrate independence from the stronger measurement key. The separately reported failing identity `Positioned child: oof-static, one hidden ancestor, hidden` remains verbatim, including the insertion oracle `[104,10,12,8]`. It is assigned to the absolute repair, not silently removed from the principal diagnostics. Parent-style and anonymous-text failure mechanisms also remain selected.

## Assertions and query order

Measurement, placement, direct-absolute and OOF-leaf tests collect all stages before assertions and validate visible references first. Their expected geometry and repeated target reads are unchanged. The fixed-size file instead retains its explicit `[24,32]` oracle, visible/show stages and block controls; it does **not** contain a separately constructed visible-reference fixture. That difference is inherited and is not a weakened assertion.

Direct-absolute tests intentionally query the absolute frame. Leaf variants remain separate fixtures: after ancestor flushes, the leaf is queried three times before any direct OOF-parent geometry query. The principal descendant variants similarly avoid a direct item query. “Leaf-first” does not mean before all ancestor queries or before any layout flush. Keeping these files separate avoids a successful direct-parent query masking clean-leaf admission.

Static absolute coordinates remain centered at x104 for width12 in the200px host starting at10; flex-end gives198. Explicit coordinates remain17,19. Leaf margins and percentages retain the previously reviewed small exact oracles. Removing Ahem from the direct absolute copy is appropriate: its participating boxes are empty and explicitly sized, with no text or baseline alignment dependency. Ahem and the load assertion remain for Range tests.

## Exclusions and limits

No known distinct repair mechanism is erased by this proposed selection. Breadth is reduced: descendant offset sizing, scroll/client-rect cross-products, prepend sizing, some two-hidden direct-placement cases, and visible-only style/text registrations remain only in the full corpus. These combinations are not proved equivalent by the compact selection. Prepend placement, nested hidden parent mutations, OOF nested leaf queries and explicit visible references retain discriminating coverage without pretending to retain every API path.

The removed columns embedding was not evidence of actual target fragmentation. The separate four true-fragmentation and sixteen provider-boundary diagnostics remain required evidence outside this partition. A calibrated failure there must be investigated; omitting it from landing files cannot establish repair acceptance.

Before landing, run the **exact hashed compact files**, retain calibration and repeated-read failures, and verify principal-only and absolute-only behavior separately. Retaining original names or exact callback bodies does not transfer browser success across changed registrations, helper removal, or font dependencies. Upstream/old-key landability and complete continuation/callback behavior also remain separate gates. No native repair is accepted by this packaging review.
