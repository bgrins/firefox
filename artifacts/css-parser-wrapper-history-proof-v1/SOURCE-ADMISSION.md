# Source admission and exact boundary

## Unchanged source

The complete parser/tokenizer and crate dependency bytes equal the authenticated public-history predecessor. `SOURCE-BINDINGS.json` retains all 70 earlier full definitions and adds full `expect_colon` and its `expect!` macro. `native/build.py` is unchanged from that predecessor; it compiles the complete crate, appending only a projected observation adapter. `wrapper_next` temporarily supplies the existing stop-before field, calls actual `Parser::next`, restores the field and records the return. It is a fixture adapter, not a proof of `parse_until`.

## Source-to-model map

| Native body | Model and derivation |
| --- | --- |
| tokenizer `skip_whitespace` byte dispatch | `WrapperWhitespace.nativeUnit`: separate space/tab, newline/CRLF, slash-star comment and stop branches. The independent `referenceUnit` enumerates the prefix grammar and uses first-terminator comment reference. `unit_refines`, positive consumption and bounded consumption connect them. |
| `advance`, `consume_newline` | Byte-position increments are explicit. CRLF consumes two bytes; FF/CR/LF consume one otherwise. Full packed line/UTF-16 state is outside this projection; existing helper components are not silently promoted to a whole wrapper-state proof. |
| `consume_comment` / `check_for_source_map` | Full native comment body retained. Prefix scan uses the accepted exact comment scan and independent directive publication; `run_annotations` proves ordered writes, including absent/present-empty fields. Heap, UTF-8 codec and normal-return assumptions remain inherited. |
| `skip_block_at_start` / `consume_until_end_of_block` | Existing active-observer cleanup precedes raw scan. `pending_none` and `skip_cleanup_complete` derive clearing and finite completion under provider progress. Pending functions and comments remain observations; the model does not erase them as whitespace. |
| `skip_whitespace` cache behavior | `run_cache`, `skip_cache` derive unchanged cached token; `run_mode` only applies to the subsequent direct whitespace/comment phase, not pending cleanup. `skip_project` composes the actual pending effects. |
| parser `next` | `WrapperNext.native` literally composes raw skip then the primary-fetch model. `second_cleanup_empty` derives why its repeated pending check is inert. `actual_fetch_join` connects to cache-aware ready fetch after skipping. Stop-before is checked after raw skip. |
| parser `expect_colon` and `expect!` | `WrapperEntry.expectColon` projects success versus error after actual next. Successful return derives non-relevant cached Colon; `declaration_entry` then proves raw skip preserves safe enable entry. Exact unexpected-token versus end-of-input error payload is not modeled by this Boolean projection. |
| save/reset/cache/enable/query | Existing same-instance cursor restoration and cache population/replay remain unchanged. `WrapperHistory`, `WrapperAnnotations` and `WrapperEpochs` compose arbitrary mixed wrapper/primary/save/reset histories and complete admitted epochs. Annotation writes have their own reference; token equality cannot imply their equality. |

## Provider and machine premises

The immutable input and same-instance saved-state contract remain mandatory. `ByteLex.read` derives Function classification from the existing name/URL components and comments from the existing comment provider. Remaining non-Function families still have individually named consumption providers. Their progress is needed to identify the finite-fuel pending cleanup with the native terminating loop; `skip_cleanup_complete` explicitly requests that premise. Bound theorems additionally require provider endpoints within the input. Raw prefix exhaustion itself follows from positive unit consumption and uses input-length fuel, not an arbitrary depth cap.

Rust inputs are valid UTF-8 strings and cursor entries must be actual character boundaries; a natural-number in-range premise alone is not Rust slice safety. This component does not derive all production UTF-8 boundaries or full metadata from arbitrary provider functions. Native pointer/reference lifetimes, usize/u32 headroom, packed-state arithmetic, allocation/normal return and compiler correctness remain premises. The proofs quantify over mathematical byte lists and natural positions. They do not prove C++ or Rust memory safety.

## Production entry and unclosed callers

The authenticated `entry-audit/` source trace identifies two production enable expressions. Its provenance distinguishes captured local files from fetched discovery files. `CALLER-SOURCE-COMPARISON.json` records a later read-only local comparison; all eight complete files, including the fetched discovery files, match the observed local bytes. The relevant substitution helper is also recorded separately. These comparisons support the static trace, not a theorem of whole current caller execution. Declaration entry is cold or passes a successful `expect_colon`; its subsequent `PropertyDeclaration::parse_into` raw skip preserves that cache condition. The geckolib substitution helper enables a freshly constructed parser. `cold_after_skip` and `declaration_entry` close the corresponding cache-entry algebra for these wrappers. The source trace includes nested-rule forwarding and supports evaluation on a fresh parser.

This is not a complete generated-property-parser theorem. `next_including_whitespace` comment filtering, callback/depth/delimiter wrappers and the declaration helper's successful-query saved Boolean/short-circuit rescan automaton remain follow-on work. The current production entry trace is static evidence, not a formal proof of exhaustive call-graph reachability or future callers. No arbitrary callback may be assumed to preserve the tracking configuration.

Late enable and query/re-enable with a relevant cached Function remain genuine library histories outside the safe epoch condition. The wrapper does not cure them. Annotation A/B replay remains protocol dependent; next raw-scans the trailing comment and can restore B where primary cache replay leaves A. No browser publication bug or ideal sourceURL contract follows from that distinction.
