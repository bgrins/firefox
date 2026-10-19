# Independent public parser history admission review

## Verdict

**Accept the scoped mathematical component and its finite native correspondence evidence.** No blocking defect found in the reviewed claims. This is not acceptance of whole-parser correctness, arbitrary observer-enable histories, complete source metadata, or a CSS annotation-publication contract. Root retains final acceptance.

Authenticated the externally supplied source FREEZE `0a290a6cbf83b6fa1be729cd13a3aeae23b77a4c6f86718baacbe0655bb83afe`, MANIFEST `a158bf5fb0be52bb3d252c69e18160e4d3e623a4650204fcff0279eea04fe75a` and checker `3d84332b8ccbb71d9271efd0bc4df35af6d8e5a894c5d8027aab2b0b06722ae7` before execution. All 208 source inputs and 110 producer-receipt inputs matched closed manifests. Replay used only the copied manifest roster and external pinned toolchains. The source snapshot matches both current local parser/tokenizer files at review time.

## Substantive proof/source review

Read all fifteen new modules, the inherited TrackingEpoch interface/proofs, admission ledger, complete primary API/observer/dispatch/comment bindings, extraction/build/driver/check code, mutation definitions and retained failures.

| Obligation | Finding |
|---|---|
| Cache coherence | `PublicCache` derives coherence from empty construction and fresh population. Key equality retrieves the deterministic read at the original key. Raw cleanup, cache hits, saving and restoring preserve the cache. The stored key/value relation is not assumed at cold entry. |
| Independent token/cursor reference | `PublicSourceOnly` reads the immutable input without a cached value or tracking mode. `PublicNext` joins pending raw cleanup and post-cleanup EOF/delimiter admission to fetch. Equality depends on the explicitly shared read provider and typed-stack primitive, not on an independently verified complete lexer grammar. |
| Actual cleanup loop | Model clears pending state, performs raw reads without replacing the public cache, pushes nested block kinds, ignores mismatched closes, and pops matching kinds. Strict provider byte progress proves byte-length fuel suffices; bounds are separately conditional on provider bounds. No universal native progress, machine arithmetic or UTF-8 safety is inferred from fuel. |
| History/epoch composition | Fetch/save/same-instance restore histories preserve cursor, saved-state, coherence and observer alignment. Each complete enable/history/query epoch requires no relevant cached Function on entry. `PublicEntry` derives this from an actually returned non-relevant token, with Colon as a specialization; constructor entry is derived. Repeated epochs still need their own entry predicate. |
| Observer matching | Function relevance follows the selected identifier/URL provider result. `FunctionMatching` independently defines per-byte ASCII case equivalence and proves agreement with lowercase matching. Non-Function families are explicitly modeled as not emitting Function effects; their consumption lengths remain external providers. |
| Annotation chronology | Separate reference carries cursor, cache key, saved cursors and URLs but no cached token value or tracking mode. It derives writes from raw/fresh source comments and suppresses writes on cache hits/reset. This intentionally models native chronology; shared comment update and key-hit policy do not independently justify an ideal annotation publication policy. |
| Source bridge | Complete 70 bindings regenerate identically. Constructor sentinel, pending flags, state-only reset, fresh tokenization/cache replacement, cache end-state restore, and tracker enable/query match the inspected source. Read-only appended wrapper does not change the original parser prefix; tokenizer bytes are exact in both compiled modes. Delimiter setter is a fixture, not a proof of parse-until wrappers. |

The independent references remove the relevant cache/mode machinery while retaining named token providers and stack semantics. Their scope is useful but conditional. In particular `byte_constructor_history` alone can run on a zero-progress abstract provider: agreement of two fuel-limited mathematical machines is not native termination. `pending_cleanup_complete` supplies the separate positive-progress condition required for the native interpretation. That separation is explicit and acceptable.

## Replay and rejection evidence

Fresh relocated replay completed with 46 modules and 371 exact named axiom reports, including 108 new reports. All reported axioms are restricted to propext, Classical.choice and Quot.sound; there are no added axioms, proof holes, native_decide or implementation replacement. Counts include concrete witness reports, not 371 distinct substantive correctness obligations.

Fourteen fixed raw-input histories yield 87 ordered snapshots in each debug/release mode. Both complete native executions match independently evaluated Lean driver output byte-for-byte. Exact ordered case/operation keys, eleven fields and complete projected records prevent dropped/extra/reordered output from being counted as agreement. The six trace corruptions reject, including None versus present-empty annotation. This corpus does not cover every family or all Unicode/metadata paths; the finite provider panics for unsupported families and only supplies whitespace runs/semicolon in the exercised opaque branches. Actual fast_match_byte and other optional feature variants are not compiled here.

All four native mutants compile and execute successfully, with intended differences: missing fresh observation (seen→off), replayed cache observation (looking→seen), reset clearing tracking (seen→off), and inverted cache key (wrong dummy token/cursor). `MUTANT-CAUSES.json` retains exact first differing records. None was accepted on incidental compiler/runtime failure. Three Lean mutants first compile concrete semantic witnesses, then fail unchanged theorems at fresh observer projection, hit nonwrite/project, or cache coherence respectively. The retained errors are semantic proof failures, not missing imports or malformed syntax.

Eight fresh integrity challenges reject before output creation: changed/missing source, shadow module, file/directory symlink, duplicate manifest key, extra directory and missing isolated mode. Duplicate-key testing updates the internal manifest seal only to exercise uniqueness; external authentication would already reject it. No shadow module executes. Producer receipts were authenticated but are not substituted for fresh reviewer replay.

## Counterexamples retained and limits

- Late enable with a relevant cached Function, and query/re-enable before cached replay, still miss the logical Function. Byte-driven Lean witnesses and native fixtures preserve both. Safe entry is a real restriction, not an assertion that all Firefox callers satisfy it.
- Reset inside a pending block raw-skips annotation A, then cache-replays B without its effect, leaving A. Both sourceURL and sourceMappingURL witnesses remain. No new browser reachability or normative last-annotation claim follows.
- Rust same-source saved states, valid indices/boundaries, immutable input, canonical codec behavior, native machine bounds and allocation/compiler execution remain admissions. Model invalid saved index is a no-op; native probe indexing requires a valid saved index. The impossible native cache sentinel requires positions below usize::MAX.
- Full line/UTF-16 metadata, actual allocated payload layout and all non-Function token payloads are projected away. Byte/pending equality cannot establish full cached ParserState equality.
- Public `next`/whitespace filtering, nested/depth/callback/try-parse wrappers and production caller entry protocols are not composed here. Arbitrary enable/query interleaving outside complete admitted epochs is not proved.
- No production code, WPT, Git, Firefox build or browser operation was performed by this review.

## Retention and cleanup

`evidence/` retains fresh commands, source bindings, all audit logs, semantic witness sources/failures, complete native rows and guard receipts. A separate receipt seal is written and verified before deleting owned generated replay/guard trees. `CLEANUP.json` records exact owned paths, file counts and byte sizes removed. Source-only package, producer receipts and review evidence remain. Replay can rebuild outputs elsewhere using `package/check.py --run --output NEW_DIRECTORY`; this review's `check.py` only authenticates retained evidence and checks its substance.
