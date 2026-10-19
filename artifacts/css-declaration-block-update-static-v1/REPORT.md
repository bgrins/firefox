# Declaration block update audit

Date: 2026-10-19. Scope: canonical parser scratch after repair 68; vector/property-id/importance coherence, CSSOM logical ordering, and actual callers. No live source edits, native build or new universal proof in this package.

## Ranked finding

**1. The special `all` setter bypasses logical-group reordering.** Root reproduced the predicted relational ordering discrepancy: eight FAIL, sixteen PASS, one harness OK, with stable source/config/binary pins. This is a diagnostic browser result with a clearly stated canonical-order premise; it is not a landed repair or a novelty claim.

For `initial`, `inherit`, `revert`, and `var(--all)`, at normal and important priority, root compares the padding-top/padding-block-start order after setting `all` on oppositely seeded blocks with the order from a fresh `all` expansion. The special `all` update preserves existing slots, so one seed keeps the opposite order. Ordinary longhand reordering and declaration-list parsing controls pass. `evidence/root-browser` contains the exact 24-subtest probe and raw results. Values, uniqueness and importance are not demonstrated broken by this order-only probe; rendering impact is not asserted.

### Independent normative argument and remaining specification gap

[CSSOM setProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty) applies a shorthand's longhands in canonical order. [Set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration) requires the updated target after existing opposite-mapping declarations in its logical group. For two such identities, the one processed later must therefore be later in the final block, irrespective of their starting order. Any fixed canonical expansion order gives convergence. The test does not prescribe whether logical or physical must be first.

[Cascade's all definition](https://drafts.csswg.org/css-cascade-5/#all-shorthand) includes both padding properties and excludes direction, unicode-bidi and custom properties. Gecko's generator deliberately lists logical properties before physical counterparts, but that implementation choice is not promoted to the normative oracle.

The gap is real: CSSWG issue [5741](https://github.com/w3c/csswg-drafts/issues/5741) remains open about defining canonical order. The relational claim assumes that a shorthand's canonical expansion order is fixed for that mapping, rather than selected from the current destination order. CSSOM's algorithm provides no destination-order input for selecting canonical order, which supports that interpretation; independent adjudication should explicitly accept it before a repair claim. Absolute cross-engine ordering is not settled here.

Historical issue [1898](https://github.com/w3c/csswg-drafts/issues/1898) discussed `all` and logical/physical setter ordering. Its actual API comments and merged [PR 2516](https://github.com/w3c/csswg-drafts/pull/2516) are retained. The 2018 closure changed setter append behavior; it neither defines the absolute `all` expansion order nor exempts `all`. Gecko's generator still references bug 1410028 and that issue. Issue 6894 is another canonical-order discussion. Thus this area has known history; no assertion of a previously unreported defect.

### Actual path and exact gap

`PropertyDeclaration::parse_into` stores the parsed all value in `AllShorthand`. `AllShorthand::declarations` and its complete iterator obtain `ShorthandId::All.longhands()`. `declare_all_shorthand` constructs the logical-first list, while generated `longhands()` applies the content/pref filter. Complete source providers are retained.

CSSOM `set_property` creates fresh scratch; `set_property_to_declarations` creates a fresh update plan, calls `prepare_for_update`, invokes the mutation closure once if needed, then calls `update`. The normal planner scans the destination backward and marks `AppendAndRemove` if an opposite-mapping group member follows the target, even when value and importance are equal.

The special all planner only checks absence/value/importance. Its executor inserts missing identities and updates existing declarations in place, never invoking the logical-order planner. Consequently changed-value and unchanged-value paths can both preserve an incorrect relational order. The root probe reproduces the changed-value path; the unchanged-value all-fast-path concern is source-derived, not separately browser-tested in this capsule.

The C++ consumers retained from `nsDOMCSSDeclaration` and `nsDOMCSSAttributeDeclaration` expose list order through IndexedGetter. `nsStyledElement::SetInlineStyleDeclaration` wraps the actual block without serialization/reparse. The mutation closure's inline-style provider asserts script cannot run at that point. A universal native bridge must still admit or prove that no callback changes the prepared block before execution; this static audit is not a proof of all scheduler/reentrancy paths.

## Negative findings and source invariants

- `push` updates declarations and importance in lockstep. A normal declaration cannot replace an existing important declaration during parsing, and a replacing declaration moves to the end. `extend` uses this policy for ordinary and all expansion. This differs intentionally from CSSOM; using `push` as the all CSSOM repair would mishandle important-to-normal assignments.
- Ordinary `prepare_for_update` assumes canonical scratch identities. Each referenced original index is unique. Reverse removals preserve outstanding original indices; ascending fixup subtracts the number of earlier removed indices. The subsequent zip consumes one declaration per plan item. No new index/importance discrepancy was found under those premises.
- The property-id set intentionally retains removed-and-to-be-reinserted identities during the internal removal phase. The full public representation invariant belongs at operation boundaries, not every statement. No external callback occurs inside the executor's removal/appending phase.
- Unique identity alone is insufficient to prove batched planner equivalence for arbitrary fabricated mixed logical/physical source lists. A metadata check finds all 94 explicitly declared shorthands have unique subproperty names and at most one mapping kind within each logical group, including Gecko-only extra subproperties. Engine/pref filtering preserves this property. Generated `all` is the important mixed-kind exception and uses the separate path. The check covers this exact metadata, not every possible future generated callback.
- The only discovered prepare call is `set_property_to_declarations`, which constructs `Default::default()` per call. The executor clears plan entries but not accumulated counters; stale-counter reuse is not a reachable defect from this caller, and those counters are not mistaken for a public persistent invariant.
- Removal deletes the identity bit, importance bit and vector element together. Longhand/custom removal returns after its unique match. Shorthand removal keeps its index when deleting, so adjacent members are not skipped; excluded properties remain. The previous duplicate-input repair is essential to this premise and is not rediscovered here.
- `new`, `with_one`, clone and clear preserve aligned storage by inspection. Equality intentionally omits the identity set because it is derived from the declaration vector; a proof must establish that relation first. No new custom-property or importance defect was established.

## Repair options and formal target

The narrow design is to reuse a per-declaration CSSOM planner for both paths. Preserve normal batching under its group-uniform source premise. For `all`, evaluate and apply each expanded declaration sequentially against the updated destination, retaining lazy expansion instead of placing `all` into the smaller shorthand buffer. Include opposite-mapping reordering in the preparation gate. No patch is supplied here.

An initial-destination `any(non-None)` gate is sufficient for deciding whether the sequential operation has any changing step: take the first initially changing declaration; every earlier initially-None declaration preserves the destination, so the first changing decision remains valid. Conversely, all initially-None steps leave the destination unchanged inductively. This relies on deterministic provider equality/identity/mapping and the planner's exact no-op contract. Do not force all setters to count as changed without checking this gate.

`DESIGN.md` specifies the next formal component and native obligations. Root owns the actual candidate, browser/build/patch gates and independent normative review. This audit contains no speculative broad finite mutation corpus.

## Replay and provenance

`check.py` first authenticates the exact manifest, then verifies source/browser pins, expected per-name outcomes, current source metadata uniqueness/group uniformity, and retained issue resolution facts. `--live` additionally compares inspected repository files with their snapshots. It executes no Firefox or imported artifact module. `SOURCE-PINS.json`, primary-spec HTML, API responses, Searchfox discovery outputs and browser evidence provide replayable dated inputs. Network retrieval and source equality do not establish universal semantics. MANIFEST plus its root MANIFEST.json/FREEZE.json are the commit roster.
