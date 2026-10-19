# Independent string-provider component review

## Recommendation

Accept the declared string transition/provider proof component and its reproducible source capsule. No substantive blocker was found. This is a universal result about the stated Lean models, supported by complete-body source inspection and finite native correspondence. It is not universal Rust refinement, full tokenizer verification, or acceptance of CSSOM serialization behavior.

The producer's 133 inputs were authenticated before executing any producer code. The independent clean relocation completed successfully. This review owns no production edits and makes no browser claim.

## Evidence independently checked

- All five new modules were read in full, including theorem statements, recursion measures, and the independent reference. All eleven inherited modules are byte-identical to the previously independently reviewed comment capsule.
- All 25 extracted definitions were read. An independent brace/comment/string scanner validates each retained source span and its exact inclusion in the executable witness. The complete actual CowRcStr module is included, including borrowed/shared construction, clone, dereference, and drop. There is no std::Cow storage substitution in this final capsule.
- Fresh relocated Lean replay passed 16 modules and exactly 152 named axiom reports, including 52 new reports. The independent audit checks the exact names and permits only propext, Quot.sound, and Classical.choice.
- Fresh debug and release Rust executables both passed the same 808 distinct cases. Independent expected-result calculation walks raw code points directly, handling CRLF and optional escaped whitespace at their source positions; it does not import the producer's preprocessing or oracle. All payloads, bad-string classifications, byte endpoints, suffixes, storage classifications, line numbers, and UTF-16 columns agree. These include 188 bad-string and 634 owned-storage cases.
- The native witness also checks actual borrowed pointer identity, clone/drop behavior, output UTF-8, return cursor boundaries, and preservation of both URL fields. The independent row oracle does not infer these native pointer/URL assertions from payload equality.
- Five changed Lean definitions compile with discriminating counterexamples, then fail the unchanged proof obligations: wrong ending quote, escaped-EOF replacement, copied NUL, dropped borrowed prefix, and consumed bad newline. These are Lean semantic mutation gates, not Rust mutation gates.
- Four source-only tamper probes reject changed model, native source, fixture, and manifest before replay output. No retained binary or .olean is needed.

Fresh logs and the exact command receipt are retained under evidence/. INDEPENDENT-CHECKS.json and AUDIT-REVIEW.json record independent checks rather than producer expectations.

## Model and source correspondence

StringTransitions has a native-shaped borrowed phase followed by an owned accumulator and a separately structured one-phase reference. The classifier theorem checks the independent quote-first/table classifier against the native branch ordering. Escapes compose the existing source-matched complete helper model; neither string-specific escaped EOF nor escaped newline is delegated to generic escape EOF behavior.

StringUTF8 proves completion at returns and at the handoff to escape processing while permitting temporary interior UTF-8 byte positions. Partial prefix/postfix copying is rejoined before a return; requiring every intermediate owned buffer to be valid UTF-8 would have misstated the native loop. Boundary.Unit is an encoding-shape abstraction, not a proof of Rust scalar decoding. Rust str validity and codec correspondence remain explicit admissions.

StringContracts derives raw quote entry, positive bounded consumption, EOF exhaustion, newline reconsumption, and the unallocated borrowed slice. Its projection intentionally drops the allocated flag for general reference equality. The native storage-mode observations and conditional borrowed-slice theorem are useful; they are not an independent universal ownership/aliasing specification.

StringTrace derives the exact consumed raw prefix and folds the inherited observer model over it. The input trace is derived from string execution rather than assumed equal. However, nativeObserved is a semantic trace interpreter, not a second transcription of every mutable Parser update. Universal correspondence between that trace interpreter and the actual Parser helper sequence remains a source-mapping admission, supported here by full body review and finite replay. URL preservation is explicit in the model, inspected in the complete native helper closure, and exercised in the native witness; public cache/reset histories remain separate.

StringAdmission proves output expansion bounds and quote-inclusive observer composition. The bounds are conditional and do not prove a Vec allocation succeeds. Native sizeof/usize representability, object limits, valid input and byte boundary, codec operations, Rc lifetime/heap behavior, and normal completion remain admitted. In particular, ParserState::advance_line_number uses ordinary u32 addition to a packed counter: line headroom and metadata normal return cannot be omitted merely because payload is the selected result. The inherited capacity lemmas retain the 30-bit line and 32-bit column bounds. The raw wrapper's opening quote must be included when instantiating whole-call bounds.

The source witness uses ordinary match dispatch and minimal Parser/Token field facades. Optional fast_match_byte expansion and full crate feature combinations are not executed by this replay. It binds the complete source definitions, not a verified compiler lowering. The current tokenizer source differs from Searchfox's indexed snapshot; the final source identity is the retained 5319a01e... snapshot. No claim silently replaces that identity with indexed upstream.

## Specification and oracle

The retained primary CSS Syntax input-preprocessing, consume-string-token, and consume-escaped-code-point sections support the selected expectations. Matching quote returns; opposite quote is data; unescaped newline returns BadString without consuming that newline; string backslash+EOF contributes nothing; escaped raw CRLF/CR/FF is removed; generic hex escape consumes at most six digits and optional whitespace, with invalid scalar replacement. A native BadString diagnostic payload is an API extension. The model's EOF tag is ghost information and does not establish an exposed parse-error event.

The independent scanner uses raw positions and an explicit loop, whereas the producer first constructs normalized code-point/endpoint records. This catches endpoint and raw newline distinctions without importing the producer oracle. The finite cases do not prove all-input preprocessing or the upstream DOMString-to-Rust-str conversion.

## All twelve original obligations

| Obligation | Disposition retained by this review |
| --- | --- |
| 1. Raw admission/dispatch | Quote-wrapper entry, progress and boundary modeled. Complete dispatcher, public EOF and iterator admission remain open. |
| 2. Preprocessing | Local NUL and CRLF/CR/FF effects covered in string semantics and independent finite oracle. Full preprocessing transducer and upstream conversion remain open. |
| 3. Borrowed loop | Arbitrary modeled byte inputs, output/endpoint and owned transition proved; native mapping and storage/heap admissions remain. |
| 4. Owned loop | Arbitrary modeled accumulator composition and partial-unit rejoining/return shape proved; native scalar codec and unchecked String conversion admission remain. |
| 5. Escapes | Existing complete helper model is composed after matching full source hashes. Codec, compiler and native integer correspondence remain conditional. |
| 6. EOF/bad newline | Modeled escaped-EOF distinction, EOF exhaustion and bad-newline reconsumption proved. No exposed parse-error/CSSOM theorem. |
| 7. Comments | Previously reviewed comment component is inherited unchanged. Its whole-native limitations remain. |
| 8. Public stream | Open: repeated ignored comments, next APIs, token cache/reset and block skipping. |
| 9. Observers | Derived string trace, both unchanged URLs and conditional location arithmetic covered. Mutable native/public-history refinement remains open. |
| 10. Native bounds | Conditional mathematical bounds are proved. usize, metadata normal completion, heap/allocation and representation assumptions remain. |
| 11. Evaluator connection | Open: actual property/selector callers and raw custom-property/CSSOM persistence. |
| 12. Replay/independence | This component's source-only, audit, mutation, independent oracle and tamper gates pass. Full provider completion is not inferred. |

## Packaging and next useful gate

PRODUCER-COMMIT-FILES.txt lists exactly the producer's 133 manifest inputs plus MANIFEST.json and FREEZE.json: 135 source/evidence files. PRODUCER-PINS.json authenticates every listed path. REVIEW-COMMIT-FILES.txt lists this independent report/checker/evidence closure. Do not stage a whole directory recursively: exclude replay binaries, generated .olean files, caches, and unrelated mutable output. The sealed producer intentionally retains some draft diagnostics as provenance; their inclusion does not count them as successful mutation gates.

A useful next proof is actual raw-dispatch/public-next admission and observer-cache/reset composition. It should connect source-derived helper calls and state restoration to these string and comment contracts, retaining allocation/codec/metadata boundaries. Additional string case counts would not close that obligation.
