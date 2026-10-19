# Actual whitespace and next wrapper histories

## Result

The new universal model derives raw whitespace/comment scanning from byte branches, composes observer-active pending cleanup with actual `next()`, and connects arbitrary finite skip/next/primary-fetch/save/reset histories to source-only cursor/token and annotation references. Cache coherence comes from the predecessor's constructor/cache transitions and is preserved by the wrappers. Safe enable entry is derived after a successful Colon, including cached Colon, and after cold raw skipping.

The implementation and reference differ structurally: native-shaped raw scanning updates parser state and comment annotations; the reference computes a source prefix and ordered comment bodies with the independent first-terminator comment grammar. Universal induction relates them. It does not define the wrapper equal to its oracle or assume a desired consumed prefix.

## Proof contents

- `WrapperWhitespace`: exact five-byte whitespace classification, CRLF, comments and EOF; independent prefix relation, cache/mode/saved-state preservation, ordered annotation updates and prefix exhaustion.
- `WrapperSkip`: actual pending cleanup followed by direct raw scan; pending clearing, cleanup completion under provider progress, coherent cache, active tracking effects, annotations and safe-entry preservation.
- `WrapperNext`: the actual two calls in `next`; derived inert second pending check; cursor/token results, tracking invariant, saved state and annotation publication.
- `WrapperHistory` and `WrapperAnnotations`: arbitrary interleaved skip/next/primary/save/reset histories, complete returned-token lists, source cursors and separate exact cache-sensitive annotation histories. Constructor cache coherence is reused unchanged.
- `WrapperEpochs`: repeated complete enable/history/query epochs under the existing non-relevant-cache entry condition.
- `WrapperEntry`: actual expect-Colon success test, cold entry, successful Colon through later raw skip, and the ensuing admitted history/query result.
- `WrapperBounds`: raw consumption and source endpoint bounds, plus pending/provider endpoint composition.
- `WrapperWitnesses`: pending Function observation, preserved opener cache, successful and failed Colon distinction, retained late-enable failure, and different primary/next annotation results. These are component nonvacuity and retained API counterexamples, not new browser defects.

Exact counts and theorem names are machine generated in LEAN-INVENTORY.json and AUDIT-NAMES.json. Counts are an inventory, not evidence that native/provider admissions have been discharged.

## Full-source finite correspondence

Ten focused histories, 69 ordered snapshots, agree between the new Lean executable and complete unmodified Rust source in both debug and release. The projection includes byte/pending state, cache token/key/end cursor, tracking mode, both Option-valued annotation fields, saved states, and operation return. Other token payloads and full line/UTF-16 metadata are explicitly omitted. The fixture's unsupported non-Function providers panic instead of fabricating consumption.

The cases specifically cover the newly modeled phases: all whitespace bytes and CRLF, UTF-8 comment content, active pending Function cleanup, cached Colon, raw comment writes, delimiter checking after skip, unterminated comment EOF, and failed Colon. Retained late-enable/re-enable and annotation A/B histories remain discriminating. Seven compiled native mutants expose dropped fresh observation, replayed hit observation, reset disabling, wrong cache key, omitted pending cleanup, cache clearing after skip and dropped raw comment publication. Three model mutants independently change whitespace classification, raw-cache preservation and pending cleanup; unchanged universal claims must reject them after compiled counterexamples establish their behavior.

The first finite fixture set did not discriminate reset-disables-tracking because no reset occurred within an active epoch. The unchanged failed comparison is retained under rejected-development; an active reset was added to the existing pending case. An attempted cache-clearing mutation in tokenizer.rs was rejected by Rust field privacy, so it was not counted as a semantic mutant. The final equivalent mutation changes the parser next wrapper after its skip call, where the field is accessible. Both failed development records remain explicit. A later aggregate audit imported two theorem-free replay drivers with conflicting global names; the retained audit failure is resolved by leaving the new driver out of the aggregate imports while still compiling and executing it separately. No theorem or audit entry was removed.

## Scope and next step

Read SOURCE-ADMISSION.md. Full metadata, character-boundary/native codec refinement, other token-family consumption, machine arithmetic, allocation and compiler correctness remain explicit. The inherited modules and counterexamples are unchanged. No production source, WPT, browser or Git operation was performed, and no new web-visible bug is claimed.

The static production audit supports the cold/Colon entry theorem; it does not complete the declaration parsing helper. The next concrete layer is callback/control-wrapper composition and the helper's saved-query Boolean across reset and rescan, including short-circuit query suppression. `next_including_whitespace` also remains a separate filtering wrapper. Those obligations are not replaced by this component's finite histories.
