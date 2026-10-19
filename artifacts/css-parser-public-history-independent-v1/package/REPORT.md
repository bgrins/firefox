# Byte-driven public history bridge

## Result and exact scope

The new kernel-checked bridge derives cached/fresh/raw/reset observations from immutable byte input, actual position-key comparison, cache population, replay and saved-state reset. Cached/fresh equality is a constructor-derived invariant, not the main premise. Function relevance is derived through the existing name/escape and URL models, including quoted URL delegation, and independent ASCII case matching.

The native-shaped operation is `next_including_whitespace_and_comments`, including its pending-block raw cleanup and delimiter/EOF gate. Arbitrary finite fetch/save/reset histories refine a cache-free cursor/token reference. Complete enable/history/query epochs refine independent logical observations when each enable has no relevant cached Function. `PublicEntry` derives this admission from an actual returned non-relevant token, including Colon. Cold construction satisfies it directly. Query returns the accumulated bit and disables tracking; a second query returns false.

Annotation publication is deliberately separate. `PublicAnnotations` maintains a source cursor and cache **key**, without a cached token/value or native mode. It derives ordered raw/fresh comment writes and no writes on cache hits or reset. Arbitrary histories agree with that reference, carrying arbitrary initial annotations. This is native effect chronology, not proof that the API matches an ideal last-annotation publication contract.

## Substance of the universal proofs

- `PublicCache`: population, key match and same-instance saved-state reset derive coherent cache values. Observer writes are separate from token/end-state storage.
- `ByteLex` and `FunctionMatching`: identifier dispatch precedence, decoded Function names, URL versus Function classification and independent case matching. Non-Function family consumption remains named provider input.
- `PublicCleanup`: typed pending-block push/pop, mismatched-close behavior and EOF; strict per-provider byte progress yields sufficient finite byte fuel.
- `PublicSourceOnly`, `PublicFetch`, `PublicNext`: independently read source tokens/cursors are preserved by cache hits; derived event lists compose with `TrackingEpoch`.
- `PublicHistory`, `PublicEpochs`, `PublicEntry`: arbitrary constructor-derived histories, complete admitted epochs, return/disable behavior and derived Colon/non-relevant entry.
- `PublicAnnotations`: exact key-sensitive raw/fresh write reference over arbitrary primary histories.
- `PublicByteWitnesses`: actual byte-input cold control, late-enable and query/re-enable failures, and sourceURL/sourceMappingURL cache-reset overwrites. These are retained known discrepancies, not newly discovered bugs.

The proof inventory has 46 modules and 371 standard-axiom audits, including 15 new modules (two are replay input/driver modules) and 108 new theorem reports. Counts describe the inventory; they do not establish the source-admission premises.

## Exact-source finite correspondence

The complete pinned Rust crate and vendored dependencies compile in debug and release. A read-only appended view exposes the projected cache, token, byte/pending state, mode, annotations and saved states. The only fixture setter supplies the existing stop-before delimiter field; it does not claim a complete `parse_until` caller proof. All original Rust bytes are retained before the appended view.

Fourteen focused input histories produce 87 ordered snapshots in each mode, compared byte-for-byte with an independently executed Lean model. They cover cold and Colon entry, escaped/case-folded names, raw nested cleanup, mismatched closers, quoted/unquoted URL, delimiter stop, EOF, query/reset/re-enable and both annotation fields. Absent and present-empty annotations have distinct encodings. The finite driver panics on unadmitted opaque providers: the corpus only needs the whitespace classifier and one-byte semicolon beyond the fully composed name/URL/comment/block paths.

Four compiled native semantic mutants change results: dropped fresh Function observation, replayed observation on cache hit, reset disabling tracking and wrong cache-key comparison. Three model mutations admit concrete kernel witnesses and fail unchanged universal proofs. The trace validator rejects dropped, duplicate, reordered, unknown, extra-field and None-versus-empty corruptions using the independent operation roster and full expected projected records.

## Counterexamples and interpretation

Enabling after a relevant Function has already been cached, or querying/disabling and then re-enabling before replaying it, can miss the Function. Those histories violate the safe-entry predicate; the component does not weaken their logical expectations or silently replay effects.

Resetting inside a pending block and raw-skipping annotation A before replaying cached annotation B leaves A. The byte model and native fixtures reproduce this known history. No new stylesheet/publication reachability or sourceURL normative contract is established here.

## Remaining work

See `SOURCE-ADMISSION.md`. In particular this does not close `next()`/`skip_whitespace` filtering, nested callback/depth/try-parse wrapper histories, arbitrary interleaved enable/query outside admitted complete epochs, all token payloads, full line/UTF-16 metadata, all non-Function consumption providers, or native codec/usize/heap/compiler refinement. Existing accepted name/string/numeric/URL components and this cache bridge must be composed for those claims; finite snapshots do not replace that composition.

No new browser bug is claimed. No production files or tests changed. Independent review and root acceptance remain separate gates.
