# Backslash/newline preservation: independent native and WPT review

## Verdict

The tested native repair is correct for the reproduced token-preservation defect. The two standalone native adaptations implement the same preservation decision under the actual tokenizer's maximal-whitespace-token contract. The initial standalone WPT packaging had two unrelated escaped-space/tab controls requiring repair 85; independent compiled extraction exposed that prerequisite. Root removed exactly those two controls. Final 30-case WPT passes; the filtered unchanged baseline has 16 FAIL/14 PASS. Both v2 two-file alternatives bind that final test and pass independent exact text application. The earlier 32-case packages are superseded.

No universal Rust translation or full CSS serialization theorem is claimed. Native and WPT acceptance are distinct from the proposed formal extension.

## Normative oracle

CSS Syntax serialization requires a reverse-solidus delimiter to retain a following newline. Backslash plus newline is not an escape; a terminal backslash instead tokenizes as an identifier containing a replacement character. Trimming the newline therefore changes a consuming grammar, rather than merely changing formatting. The `animation-name` grammar admits identifiers/strings or none, not a backslash delimiter. Substitution of the invalid token sequence yields initial `none` because the property is noninherited. See PRIMARY-SOURCES.md for the independently checked current primary sources and retained section identity.

The test calibrates literal validity with CSS.supports for each case. Every target has a valid initial name, the tested value, restoration, and a second tested update. There are four newline spellings, two prefixes and three suffixes: sixteen terminal-newline failures and eight comment-ending invalid controls. Eight valid-name controls bring the first test to 32. No absent animation, unsupported feature guard, screenshot or previous-valid-declaration fallback is used as the oracle.

## Complete changed-path review

Read the retained complete VariableValue constructor, parse_declaration_value and recursive parse_declaration_value_block. In the tested integration, trailing whitespace is counted only when the previous outer token was not DelimBackslash. Each iteration then records whether its token is DelimBackslash. A retained backslash/newline run leaves the ordinary last-token metadata as WhiteSpace, which matches its stored suffix. Existing exact-length and last-nonwhite metadata handling still applies to ordinary trimmed suffixes. Reference ranges and nested fallback descriptors are untouched.

The standalone variants return a third boolean from both scanners and discard it at the fallback call. They update the boolean only on non-whitespace tokens; only the outer constructor uses it to suppress its existing ASCII trim. Thus comments and ordinary tokens reset preservation; nested parser state cannot leak into the outer state. No provider, substitution function, EOF repair, global serializer or generated representation changes are added.

The flags are equivalent at the decision point because consume_whitespace consumes the whole raw run, including CRLF, spaces and tabs. A terminal WhiteSpace token therefore has at most one immediately preceding nonwhite token. The tokenizer emits DelimBackslash only when followed by a newline; a standalone backslash at EOF is an identifier path. Without these premises a synthetic stream [Backslash, WhiteSpace, WhiteSpace] distinguishes the flags. This is a real source admission, not an unconditional Boolean equivalence.

The standalone variants intentionally retain each base's old trimming and EOF behaviors. They do not become equivalent to the entire integrated constructor. In particular, escaped SP/HT inside a nonwhite identifier still loses its final byte without repair 85. That explains the two unrelated controls found during this review; it does not make repair 85 necessary for the sixteen backslash/newline failures. Neither standalone source has been isolated Firefox-built or browser-tested. The v2 HEAD base already includes repair 83; its #86 patch does not add that repair. The upstream base excludes 83/84/85. The only HEAD v1→v2 constructor delta is the already accepted leading-origin normalization; its scanner/preservation adaptation is unchanged.

The tested source is c0e7a18b9cb5104f6097178460924e163e30b66a178dd5ae3adb08fc96c30b73. The baseline is 8f166d5cbd25d298a34d820e148c8967d3b0b0fc009a371831d4e4be336548d7, already including repair 85. The only additional recorded production formatter change is a function-signature line wrap in properties/mod.rs; it changes no expression, type or control flow.

## Independent execution and raw evidence

`check.py` authenticates the retained external evidence, reconstructs outcome maps from raw browser events, and verifies unique keys. First paired suite:16 FAIL/16 PASS becomes32 PASS; all 435 prior status/message pairs are identical; 467 subtests and 24 OK harness records total. Before/after source, test and binary pins agree. The build log reports success despite the separately retained known Mach export-monitor KeyError; dedicated WPT lint has zero errors/warnings. The initial and final v2 two-file patches independently apply as text to their exact retained bases and reproduce the candidate source and test hashes. Root's temporary-index apply/reverse receipts supply the Git-tree evidence; this reviewer did not mutate Git.

A fresh artifact-local Rust replay compiled the actual full cssparser crate and 22 complete extracted source items per variant, including the complete constructor and recursive scanners, for baseline/tested/HEAD-alone/upstream-alone.73 cases per variant all parse and substitute without panic. Raw rows and extraction bodies are retained under native-receipts. They cover LF/CR/FF/CRLF, mixed whitespace, comments, nested blocks, fallback parsing, EOF repairs and the escaped-whitespace distinction. In the first 56 structured cases, the checker derives expected stored bytes independently from the chosen suffix. Both standalone variants preserve the sixteen targeted runs. The tested integration also preserves escaped whitespace while the two standalone variants demonstrably retain the old defect.

The reused origin companion supplies a pinned cssparser dependency closure and adapters. Gecko atom/namespaces/style/unit/provider types are facades; substitution lookup is deliberately partial (signature plus actual fallback tail), with missing/known synthetic provider values. These native rows establish constructor/scanner behavior with actual tokenization, not whole Gecko lookup or browser rendering correctness. The browser evidence independently covers the real consuming property. This review adds no theorem-count claim.

## Proposed formal extension

Extend the accepted terminal-span component with a distinct Backslash delimiter kind, not just generic Other. Define an independent retained-prefix policy that keeps an entire terminal WhiteSpace token after Backslash and otherwise drops only terminal WhiteSpace. Prove source-shaped immediate and persistent flags agree under coalescing and delimiter-followed-newline validity, together with exact raw byte prefix and first/last metadata results. Keep CRLF raw lengths, comments, escaped SP/HT, nested outer-block summaries, fallback flag disposal and EOF compatibility explicit. A no-coalescing counterexample and omission-of-preservation witness should prevent vacuous equivalence. Full tokenizer correctness, arbitrary retokenization, provider evaluation and browser scheduling remain outside that component.

## Reproduction

Run `python3 -I -S check.py` for retained evidence comparison. `native_replay.py --output ABSENT_EXTERNAL_DIRECTORY`, also with `python3 -I -S`, authenticates the origin dependency manifest and source inputs before loading its lexer helper, then rebuilds the four source extractions. This is a local review using pinned sibling artifacts, not an independently vendorable capsule. Completed generated binaries are not part of the review roster.

Final test SHA256: ae9f9029d7dfefad6b35acd0946f2cbfb19520d562d20e6897c056a8622efcfe. Final HEAD patch SHA256: 2f043cfb693a9608f89034a8e36e9165a18041003df3a386dc4bd1e7ba849b03. Final upstream patch SHA256: dc959eb6ec17c4aaf5979bf76e5b7ebd7674307a3102412199228105337f46b7. Final 30-case baseline is a filtered retained run, not a newly executed original-browser run.

Packaging metadata note: the initially inspected PACKAGING-v2 limits sentence incorrectly said both bases exclude repair83. This review uses the actual pinned source bytes and the accurate base distinction above. PACKAGING-v2.json is intentionally not an immutable review input; its prose can be corrected without changing any reviewed source, test or patch.
