# Resolved relative-unit summary repair

## Candidate and contract

The candidate changes only `servo/components/style/custom_properties.rs`. The general constructor remains byte-identical. A private constructor initializes the same value, then installs a complete token dependency summary when available. Exactly two persistence calls use it: the attribute branch of `substitute_references_if_needed_and_apply`, and the universal branch of `Substitution::into_value`. Existing taint updates, CSS bytes, URL data, token metadata, reference lists, namespace/cache selection and parser context are untouched.

The exact scanner agrees with the independently reviewed suffix-parser proposal after renaming and removing a comment. It repeatedly creates the actual cssparser Parser at the remaining suffix, reads one complete lexical token and advances by the consumed byte count. Only Dimension tokens reach the unchanged native `ReferenceFlags::from_unit`. Escapes are decoded by the tokenizer. There is no recursive descent or arbitrary nesting cutoff; nested opening and closing tokens are traversed in source order.

Recognized unresolved var/env/attr functions, BadUrl and BadString return None. This preserves the old empty References at the two sinks. In particular arbitrary environment link parameters can still contain unresolved functions; this domain is explicitly unrepaired. Earlier accumulated flags are not installed on None. The helper does not validate balanced syntax or establish caller validity. It adds a scan of the final value; no performance-neutral claim is made.

## Source and standalone evidence

`original/custom_properties.rs` is the current source snapshot, SHA 9a508880b8037baf5c6bfbbaadbcc2da0ac869e683c0aded403df60a7df75da4. `prepare.py` deterministically constructs the complete candidate and minimal native patch. The checker regenerates both, verifies that removing precisely the helper/constructor and undoing two call renames reproduces every original byte, applies/reverses the patch, and matches the independently audited helper.

The Rust harness compiles the retained actual cssparser crate and its source dependencies offline. It extracts the exact candidate helper, native bitflag block, native `from_unit` body and all twelve unit constants. Forty-nine independently specified token examples distinguish every unit, nested calculations, escaping, inert strings/comments/URLs, separated tokens, malformed lexical tokens and unresolved recognized names. A separate 300,000-level nested input executes on a 64 KB Rust thread stack. This tests the real scanner, not a Python translation.

The small harness supplies the ReferenceFlags wrapper derive and a from_ident adapter matching the retained style_derive template and native enum. It does not compile the complete Stylo derive macro or Stylo. cssparser's optional fast_match_byte/fast_match_color features and Gecko-specific allocator/measurement derives are disabled. This is source-bound scanner testing; the Gecko feature configuration still requires root's native build. Rustc identity is pinned in scanner/TOOLCHAIN.json. No generated objects or executable is required in the capsule.

## WPT proposal

`wpt/attr-resolved-unit-dependencies.html` contains 21 synchronous subtests. The first three preserve the independently retained browser failures: attribute font-cycle detection, universal-chain font-cycle detection, and attribute ordering with an explicit local font size. They expect registered initial 11px / inherited font 23px for the two cycles, and local 17px for the acyclic case.

Additional cases cover absolute/literal controls, escaped dimensions, nested calculations, local lh ordering, distinct rem/rlh root bases, an inherited substituted universal value, comments, token separation, and inert strings/URLs. Explicit root font/line-height values are 19px/29px; parent font is 23px; local font/line-height are 17px/31px. Assertions use CSSOM values rather than font metrics or pixel rendering. URL cases have no attr-taint and never fetch the custom URL. String and URL values are invalid for font-size, which consequently inherits; their registered values must remain intact, distinguishing a spurious cycle. There are no timers or external font resources.

The 1/**/em control is a valid token sequence but invalid registered length. Its registered property defaults to 11px, then font-size consumes that 11px; it must not manufacture a font-relative dimension. The scanner does not promise property-syntax validity.

The checked-in WPT bytes are fixed for the root's exact baseline/candidate comparison. JavaScript syntax and all 21 distinct registrations are checked here without executing callbacks. Browser results and native compilation are not claimed.

## Normative oracle and limits

The current Properties and Values API dependency-cycle rules connect registered relative lengths to their font/line-height bases. Registered values are computed before substitution into ordinary properties; a cycle invalidates the involved values. The retained design and scanner audit provide the full source/spec trace. Primary references: https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles and https://drafts.csswg.org/css-values-5/#attr-substitution. The supported-name/computation rules explicitly include strings and URLs: https://drafts.css-houdini.org/css-properties-values-api-1/#supported-names . CSS Syntax tokenization distinguishes dimensions from string/comment/URL contents.

This repair restores selected output metadata. It does not prove substitution selection, serializers, graph construction, Tarjan correctness, all environment payloads, native allocation behavior or all CSS. The separate Lean model is not represented as a proof of this complete Rust tokenizer or the whole graph. Previous language/ownership/formal obligations are unrelated and unchanged.

Remaining gates are independent exact candidate review, root Gecko build, final formatting/lint, exact-byte paired WPT and suitable existing regressions, and final standalone packaging against the root's commit base. No live sources, WPT files, index or Git references were changed here.

## Completed isolated replay

The fresh copied-source replay passed all source/patch/JS gates and the actual 49-case scanner plus 300,000-level/64 KB stack case. `evidence/scanner-replay-result.json`, commands, compiler log and source-binding hashes retain the result. A development checker initially reconstructed one extra newline while undoing the inserted helper; that checker-only defect was fixed before this replay. Candidate/WPT bytes were unchanged. Root browser baseline results are external to this sealed capsule.
