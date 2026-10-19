# Independent review of tokenizer byte-dispatch admission

## Scoped verdict

The frozen v2 component is accepted for its stated conditional byte-dispatch scope. The frozen v1 current-table result is also supported. The Lean component proves first-match preservation for its abstract table builder. Its source binding covers all 22 retained invocations and all 256 byte values per invocation. This does not prove Rust macro expansion, compilation, full tokenizer semantics, native progress/UTF-8 invariants, or the resolved dependency scanner end to end.

One concrete tooling limitation prevents treating v1's extractor as a general future-source admission gate: it accepts multiple named wildcard bindings within one invocation, while the actual macro rejects the second binding. This does not invalidate any of the current 22 invocations; each has at most one. V2 fixes this admission gap and the offset labeling; its source and Lean semantics are unchanged. No blocker remains for the stated component scope.

The review author did not author the capsule or its Lean modules. All producer inputs were authenticated against the supplied FREEZE and MANIFEST hashes before executing its extractor/checker. Independent source inspection, a separate inventory/classifier, fresh kernel replay, relocation, source tamper rejection and targeted reader mutations supplement the producer replay.

## Obligations and results

| Obligation | Verdict and exact limit |
| --- | --- |
| Abstract table construction | Accepted: induction follows forward arm enumeration and preserves preexisting entries. No admission predicate or circular equality premise is used. |
| Ordered reference | Accepted mathematical reference: recursive first matching pattern. It shares the mathematical coverage predicate with the builder; source-pattern lowering is a separate finite obligation. |
| Index bounds | Accepted: selected ID lies in the enumerated arm interval; zero start plus at most 256 arms gives a byte-sized ID. Current maximum is 29 arms. |
| Inclusive range | Accepted for the model and admitted source patterns; actual macro loops lo..hi then inserts hi. Current source has only valid ascending inclusive ranges. |
| Actual 22 call sites | Accepted as a retained-source audit: independent lexical masking finds the same invocation boundaries/hashes, including nested calls. There are 19 tokenizer and three serializer invocations. |
| 5,632 current decisions | Accepted exhaustive finite source evidence plus kernel computation: all byte values are covered, and the independent source matcher agrees with each table. This is not a universal Rust parser proof. |
| Named bindings and body selection | Current source passes: at most one named binder per invocation, with u8 input. Expansion's outer binding, enum/table naming and unchanged body splicing require Rust/syn/quote/compiler correspondence; the theorem concerns selected arm IDs. |
| Supported future grammar | v1 limitation: two named binders are admitted by extractor but rejected by actual macro. Guard and exclusive-range mutations reject as intended. Exact current source remains admitted. |
| Semantic mutations | Accepted negative evidence: overwrite changes cause an unsolved preservation goal and false decidable witnesses; exclusive endpoint changes cause the inclusive-range obligation and witnesses to fail. No parser/syntax error accounts for rejection. |
| Restart/progress/provider audit | Appropriate open ledger, not kernel closure. Fresh state excludes block skipping/cache reuse, but full provider return-boundary, arithmetic and lexical payload proofs remain open. |
| Native correspondence | Conditional source refinement only. No Rust compiler, macro expansion executable, Gecko build or browser ran in this review. |

## Proof review

`table_refines_ordered_match` is a structural induction over the finite pattern list. Its induction hypothesis permits arbitrary starting ID and prior table, which is necessary for the accumulating builder. The present/absent prior-entry split and coverage split establish the recurrence directly. `fresh_table` specializes an empty table; `retained_entry` is a consequence rather than a second assumption. `selected_id_bound` proves the enumerated range by induction, and `selected_id_byte` derives representability from the list bound. `inclusive_range` computes singleton coverage.

There are six general theorem audits and two concrete counterexample audits. The producer RESULT field calls all eight `universal_theorem_audits`; that field should be read as eight theorem dependency audits, not eight independent universal semantic results. Generated Lean adds 22 current patterns, 22 arm-count checks, 22 exhaustive byte-table checks and 22 instantiations of the generic builder theorem. Counting these instantiations does not multiply the independent mathematical result.

The successful modules use no sorry, admit, custom axiom or native_decide. Audited dependencies are standard propext/Classical.choice/Quot.sound only. Failed mutant compilations print sorryAx for declarations with failed proofs; those outputs are negative evidence and are not imported into successful modules. The pinned Lean executable and normal Lean/Std distribution remain trusted toolchain premises.

## Source lowering and independent checks

Producer lowering tokenizes retained Rust source, extracts arm patterns, and lowers byte literals/inclusive ranges/OR/wildcards to numeric intervals. Its direct textual matcher has a separately implemented byte-escape decoder and does not consume those numeric intervals. However, both paths share the invocation/arm extraction and source boundary selection. Their agreement alone is not independent evidence for that shared segmentation.

The review's `audit_tables.py` does not import producer code. It separately masks strings, character literals and nested comments, discovers and balances the macro invocations, and compares their complete source hashes. It recomputes membership sets directly from original pattern text and checks first-containing-set IDs for each byte. Its independently checked inventory and 5,632 decisions match. This remains an unverified source reader, deliberately scoped to the frozen sources; it is additional audit evidence, not a formal Rust grammar implementation.

The actual macro's `get_or_insert` maps to preserve-existing insertion. Its ascending per-arm enumeration maps to `build`. Recursive OR insertion has the same coverage union because each disjunct inserts the same ID and does not overwrite. Wildcards fill all remaining entries; current tables have no uncovered byte. Source parsing enforces ascending endpoints; byte literal decoding and the native u8 input domain constrain intervals to 0..255. The abstract Nat function and Option Nat table are representations, not native arrays.

Native refinement still relies on: Rust byte-literal and syn pattern meanings; syn parsing of the exact source; get_or_insert behavior; u8/isize/usize casts for the bounded values; 256-element array construction/indexing; enum variant/discriminant emission; expression evaluation exactly once; binding scope/hygiene and copied arm-body semantics; quote output and Rust compilation/optimization. These are explicit primitive/representation obligations. The finite decision check reduces arm-selection uncertainty under them; it does not eliminate them.

## Concrete findings retained

### F1: v1 accepts multiple named wildcard bindings

In `serialize_name`, replace the first `b'\0' => Some("\u{FFFD}"),` arm with `other => Some("\u{FFFD}"),`, keeping the final `b =>` arm. The extractor still exits zero and emits 22 invocations/5,632 decisions. Actual `parse_pat_to_table` sets `wildcard` for `other`, then its assert_eq(*wildcard, None) fails on `b`. The witness is retained under `reader-probes/two-bindings/`.

This is a source-admission-tool limitation, not a current native/browser defect. It motivates rejecting more than one named binding before generation. The initial source's maximum is one. A guard mutation is separately retained under `reader-probes/guard/` and is rejected.

### F2: v1 offset field naming

`byte_start` is a Python Unicode string index. All 19 tokenizer invocations have different actual UTF-8 byte offsets because earlier comments contain non-ASCII characters. The source slicing/hashing uses the same string indexing, so invocation hashes remain correct. Treat this as a character offset, not a binary seek offset. TABLE-AUDIT.json records both values. It does not undermine the proof or inventory.

## Whole-tokenizer and scanner limits

The complete macro and source configuration show default fast_match_byte selection and the unoptimized match alternative. This component is useful precisely because the unoptimized native scanner harness cannot by itself validate the optimized macro. It still does not establish full lexer outputs. Numeric conversion, name/escape handling, owned-buffer validity, URLs, comments, strings, invalid tokens, UTF-8 return boundaries and successful token progress need their own refinement.

The source witnesses correctly reject overly strong helper assumptions: advance may temporarily stop inside a UTF-8 scalar; quoted URL lookahead can return without movement; unadmitted consume_name input can be empty; ordinary public next skips pending blocks and is not a flat raw-lexer reference. Prefix progress and actual caller predicates are required. Line/column arithmetic and global input-size admission remain open; a local substitution size guard cannot establish a universal persisted-string bound. The ledger does not silently replace missing admission with empty output or vacuous input exclusion.

No browser/compiler result, all-tokenizer closure, universal CSS correctness or original full C1–C13 closure is inferred from this component.

## V2 delta verdict and retained replay

V2 FREEZE `5054b4b8769cd6ac2f35bcc86ce5371a69efd007ecfcbf9a3e978e33e6a34f66` and MANIFEST `c014113cbe91c76e52cf27a07f4407432a660cf73a83e436871f4a242491a137` were independently authenticated before execution. All retained original Rust/Cargo files, ByteDispatch.lean and generated CurrentInvocations.lean are byte-identical to v1. V2 changes extraction validation/coordinates, checker regressions, descriptions and retained provenance/receipts.

The new per-invocation named_bindings list rejects a second identifier pattern while excluding `_`. The admitted grammar only permits a standalone identifier, so this check covers every named-binding form accepted by that reader. It matches the actual macro's one-binding assertion for the supported grammar. It does not claim to implement arbitrary Rust pattern/name resolution. The exact v1 witness is rejected with the expected `multiple named bindings` diagnostic in the fresh v2 replay.

`source_character_start` now identifies the string-slice coordinate and `byte_start` is the UTF-8 prefix length. The checker verifies their relation against raw bytes. Tables, invocation/body hashes and semantic Lean input are unchanged. F1 and F2 are fixed for this capsule; v1 and its counterexample remain immutable.

Both v1 and v2 were compiled fresh using the pinned Lean executable. Both relocated replays passed, with new output paths and regenerated source tables/modules. V1 native-macro-source tampering and v2 extractor tampering were rejected before an output directory was created. Both semantic proof mutants fail on semantic obligations. The independent inventory/membership audit passes for v2 too. These checks establish reproducibility and useful failure sensitivity; they do not substitute for the source/proof review above.

The review's checker authenticates this entire retained evidence set and rechecks the independent source inventory. `--replay --lean PATH --output NEW_DIRECTORY` additionally runs a new producer v2 kernel replay after authentication. The pinned executable is `/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean`, SHA-256 `d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf`. Python 3 and the matching Lean distribution are required. Compiled .olean outputs from review runs are omitted; source modules and full command/results are retained so the kernel gate can be rerun from source.
