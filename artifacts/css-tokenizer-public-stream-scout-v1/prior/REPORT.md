# Comment loop and observer component

Status: source-bound mathematical component, awaiting independent review. This does not complete the string/comment provider or the full tokenizer. The unchanged twelve obligations remain in PROOF-TARGET.md.

## Result and independence

Seven new Lean modules prove the complete modeled comment-body execution against independent observations for arbitrary finite byte input, initial mathematical location and URL state. `CommentExecution.raw_reference` admits the raw `/*` prefix itself and rejects other prefixes; it does not assume an already prepared comment payload. Rejection is a totalized model wrapper, not behavior claimed for an illegally called native helper. Opening progress, first terminator or EOF, exact raw body, consumed prefix, location and both URL fields are included. A `closed` bit and an accumulated body list are ghost results; native code returns a borrowed slice, and the exact-body theorem connects that slice projection.

The first-terminator reference builds adjacent-byte marks and finds their first true index. It does not invoke the recursive scan. The reference observer folds one byte at a time with a pending-CR bit, rather than using the native CRLF grouping. A further theorem relates that fold to whole encoding units and their UTF-16 widths. Directive reference code parses marker and space, consumes an independently listed literal header, and uses a separately specified whitespace set. The native model uses whole-header prefix tests. Arbitrary update histories, unchanged-field preservation and empty-value overwrite are proved. None of these equivalences takes trace equality as a premise.

The retained full native functions are manually related to these models in SOURCE-MAPPING.md. Their byte-for-byte extraction is replayed, and finite debug/release execution checks that mapping. This is not a verified Rust compiler, automatic verified Rust-to-Lean translation or universal theorem about a compiled Firefox binary.

## UTF-8 and arithmetic

The mathematical byte model is unrestricted. Native admission requires a valid Rust `str`, an actual character-boundary cursor and sufficient remaining bytes for the opening. `Boundary.Unit` is deliberately a broader encoding-shape type than valid Unicode: a non-continuation head with the appropriate number of continuation bytes. Theorems establish complete-unit boundaries for the returned body, remaining input and directive URL; the connection from Rust valid strings to these units, scalar decoding, and UTF-16 length remains an explicit codec premise. No malformed byte list is executed through the Rust facade.

Native location storage is not silently modeled as unbounded. The module proves column arithmetic projections modulo 2^32, packed-line division and increment properties, and conservative sufficient bounds: initial offset plus consumed bytes below usize capacity, initial line plus bytes below 2^30, and initial column plus twice the bytes below 2^32. Apply these to the complete consumed prefix including the opening. Valid initial packed low bits and correspondence of the projected starting location are required. Intermediate adjusted line-start storage can wrap even on short non-ASCII input; the modular column lemma accounts for it. The package does not claim natural-line behavior at packed-line overflow. A small extracted-source boundary fixture checks all four low-bit values at the 30-bit line limit: debug panics, release wraps. Further fixtures check the actual four-byte-intro line-start wrap and the usize-to-u32 column cast without huge allocations.

## Fresh executable checks

The observer generator retains eighteen complete function bodies, including `consume_comment`, `check_for_source_map`, both slices, all byte access helpers and all location helpers. The witness uses small layout-compatible type facades and an ordinary Rust `match` macro. It checks 395 histories comprising 405 comment calls in both debug and release: first terminator/EOF, exact borrowed slice address and contents, byte cursor, UTF-16 column/line, valid returned boundary and both URL fields after every call. It covers modern/deprecated markers, all five whitespace delimiters, Unicode and NUL raw values, empty overwrites, unmatched preservation and unterminated directives. A Python regex/header reference and independent codepoint location reference generate expectations. These finite checks are native agreement, not a universal source theorem. The earlier 646-case static witness did not assert URL fields and is not counted as such evidence here.

The Lean closure has eleven source modules: seven new modules with 62 theorem audits and four unchanged helper modules with 38 inherited audits. The 100 audits permit only Lean's standard `propext`, `Classical.choice` and `Quot.sound`; some theorems use no axioms. Counts describe inventory, not proof strength. No new axiom, placeholder or native-decide proof is used. Four altered definitions compile together with concrete inequality witnesses, then fail the unchanged theorem suites: wrong terminator byte, wrong four-byte UTF-16 width, missing form-feed delimiter, and cross-writing the source URL from the mapping URL. Their failures must be semantic rather than syntax/name errors.

## Obligations preserved

| Original obligation | Component result / remaining work |
|---|---|
| 1. Raw admission and dispatch | Raw opening totalization and UTF-8 return boundaries proved. Full actual dispatcher/public-entry guards and upstream byte conversion remain open. |
| 2. Preprocessing | CRLF/CR/FF location fold and encoding-unit relation proved. Raw payload is intentionally preserved. Full spec preprocessing/endpoint-map relation, including NUL replacement outside ignored comments, remains open. |
| 3. Borrowed string loop | Open; unchanged source and static audit retained. |
| 4. Owned string loop | Open, including partial UTF-8 copying and unchecked conversion. |
| 5. Escape composition | Existing helper files preserved and audited, used only for width/boundary support here. Complete string/escape caller composition remains open. |
| 6. EOF versus bad newline | Comment EOF covered; string EOF and bad-newline returns remain open. |
| 7. Complete comment loop | Universal model result for first raw terminator/EOF, raw slice, endpoint and opening progress. Native bridge is source inspection plus finite extracted execution under the stated primitives and bounds. |
| 8. Public stream composition | Open: ignored versus preserved comment APIs, cached tokens, reset and block skipping are not modeled by direct helper histories. |
| 9. Observers | Complete modeled direct-call location and both URL updates, body-history equivalence, UTF-8 boundary properties; actual direct consecutive-call histories tested. Cache/reset history behavior remains open. |
| 10. Native bounds | Explicit arithmetic lemmas and sufficient domain proved. Rust memory, allocation, usize representation, primitive operations and actual representation admission are external. Beyond-bound natural-location behavior is not claimed. |
| 11. Evaluator/CSSOM | Open. No property/selector/custom-property persistence or serialization closure. Expected-failure context remains distinct. |
| 12. Replay/independence | Source-only regeneration, fresh kernel compilation, axiom audit, compiled semantic mutants, relocation and tamper rejection gates supplied for this component. Full-provider replay awaits the open components. |

No native repair, new browser defect, performance result or novelty claim is made. Parent owns acceptance and optional browser controls.
