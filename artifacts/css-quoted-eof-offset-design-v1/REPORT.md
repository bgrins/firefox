# Quoted EOF fallback endpoint repair

## Finding and repair

The current `VariableValue::parse` removes one final backslash after `parse_declaration_value_block` has recorded substitution endpoints. For `var(--absent, "example` followed by one backslash and EOF, the stored outer endpoint is 25 but the recovered CSS has 24 bytes. `do_substitute_chunk` eventually slices beyond that string. Root independently reproduced the corresponding browser crash; this capsule reproduces it using extracted source.

The candidate records the existing deletion decision while visiting the terminal quoted token. Every enclosing reference subsequently constructed subtracts that one byte. The final serializer applies exactly the recorded deletion. References completed before that token keep their endpoints. The patch preserves serialized bytes, including two separate existing defects: even terminal backslash runs and escaped terminal quotes. Those require separate repairs.

`NATIVE-FREEZE.json` binds the original and proposed complete file, patch and generator. Root owns formatting, Gecko compilation, exact browser pairing and final acceptance. This capsule does not claim those gates have completed.

## Source and caller trace

`PropertyDeclaration::parse_into` skips initial whitespace before invoking custom-property parsing. `VariableValue::parse` captures that starting position and calls `parse_declaration_value`, which uses `parse_until_before` for top-level declaration delimiters. Each substitution creates its reference slot, recursively parses fallback contents, and records its end after synthesizing any missing parenthesis. Nested fallback references are in their own `References` vector; enclosing references complete after descendants. Ordinary nested blocks share the same recovery state.

A quoted token requiring a synthesized quote is terminal: actual cssparser string consumption either returns at its matching quote or consumes to EOF; unescaped newlines produce `BadString`, which this parser rejects. A terminal backslash belongs to that token. No later source token can introduce a new reference start or fallback start beyond it. The recovery quote is the first synthesized character on this path; existing comments/URL/identifier EOF recoveries also consume EOF and cannot precede another real quoted token. These are source admission arguments, not a kernel proof of the complete cssparser implementation.

Thus all pre-existing starts remain valid, earlier completed endpoints precede the deleted byte, and every enclosing endpoint is source length plus the cumulative synthesized suffix length. `reference.end - 1` still excludes precisely that reference's synthesized closing parenthesis. The code changes endpoint construction, rather than decrementing an already-built whole reference tree.

The standalone harness calls actual `Parser::skip_whitespace` before parsing, preserving this caller prerequisite. It does not claim correctness for arbitrary external calls whose leading trimming was not reflected in `input_start`. Top-level delimiter handling remains actual cssparser behavior. Arithmetic/UTF-8/source-position validity, normal parser metadata updates, allocation and compiler behavior remain native assumptions.

## Executed source and boundaries

The source-only runner builds the complete pinned cssparser crate and its vendored dependencies. It extracts complete `VariableValue::parse`, `empty`, `push`, both declaration-value functions, `parse_name`, `do_substitute_chunk`, `substitute_internal`, `ReferenceFlags::from_unit`, the relevant structures, and `Substitution::new/from_value`. Extraction records include full-body hashes and offsets.

`substitute_one_reference` is deliberately a provider boundary: its complete source is retained and hashed, but only its exact signature and final missing-provider fallback tail are compiled. A small provider supplies missing values or a named present value. Namespace parsing is rejected by a panic if reached; the attribute-type facade admits only omitted type before comma/EOF. Atom/map/taint/context storage and the derived var/env/attr recognizer are declared facades. This validates shared fallback slicing, not DOM attribute lookup, environment selection, cascade scheduling or whole provider semantics. No claim of memory safety follows from ordinary safe-Rust execution alone.

Forty cases cover two quote kinds; var/env/attr missing-provider fallbacks; closed and missing delimiters; odd/even terminal backslashes; escaped quotes; nested references and blocks; preceding siblings; leading whitespace; UTF-8 text and a present primary value. Original: 22 caught panics, 18 successful controls. Candidate: 40 successful operations, byte-identical stored CSS. A native mutant removing only the endpoint correction restores the original 22 panics. Earlier sibling endpoint 19 remains 19. The two string-content defect families remain diagnostic, not semantic successes.

## Kernel component

`Endpoints.lean` independently defines the boundary map for deletion of one byte. Ten audited theorems cover unaffected earlier endpoints, shifted enclosing endpoints, no-edit preservation, exact serialized-prefix lengths, bounded nested endpoints/fallback slices, arbitrary enclosing and sibling lists, and the original out-of-bounds witness. The model assumes the source-derived terminal-token and cumulative-suffix premises described above. It does not pretend that these arithmetic theorems prove the recursive parser itself. A semantic model mutation omitting the subtraction is rejected.

## Spec and prior issue

CSS Syntax returns the string token at EOF and ignores a final backslash whose following input is EOF; function consumption also completes at EOF. This supplies a valid recovered string/function value, rather than grounds to reject the declaration or crash. [CSS Syntax string consumption](https://drafts.csswg.org/css-syntax-3/#consume-string-token), [function consumption](https://drafts.csswg.org/css-syntax-3/#consume-function).

Missing custom properties select their fallback, which is recursively substituted. The isolated absent-provider case follows that path. Tests should compare the resulting semantic value with an explicit terminated literal, avoiding unrelated disputes over raw custom-property serialization. [CSS Variables substitution](https://drafts.csswg.org/css-variables-1/#replace-a-var).

Bug 2013337 comment 19 describes a related fallback-boundary crash caused by incorrectly treating an inner rgb() closer as the outer closer. Its source-position-based fix is already present here. The current failure instead comes from deletion after endpoint construction. This is a bounded novelty check, not an exhaustive duplicate search. [bug 2013337 comment 19](https://bugzilla.mozilla.org/show_bug.cgi?id=2013337#c19).

## Composition and remaining gates

The parity repair should strengthen the single `removed_backslash` recording predicate to odd terminal runs; it must not change only the final pop after this patch. The escaped-quote repair changes the quoted-token closure test. Keep each standalone original-source proposal and the combined adaptation explicit. Root's endpoint WPT should retain quote kinds, var/env/attr, nested fallbacks, earlier siblings, carrier variables, present primaries and closed/no-backslash controls. The two other semantic defect families should remain separately reported until separately repaired.

Remaining: independent exact-source/lemma review, root Gecko build and exact WPT pair, final source/checksum/lint/commit packaging. Full CSS/tokenizer/provider/caller verification remains outside this narrow companion and is not marked complete.
