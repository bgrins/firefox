# Escaped trailing-space corruption

**REACHED; locally reproduced.** Separate preexisting byte-trimming defect, not introduced by the reviewed trailing-token metadata patch. No repair has been implemented.

## Primary oracle

CSS Syntax consumes backslash followed by an ordinary space as that space, appended to the identifier. Declaration parsing removes trailing whitespace *tokens*, not a space within an identifier. Substitution returns component values; it must preserve that identifier. Therefore substituting the custom value `x\ ` into animation-name must agree with the same literal token. See [escaped code points](https://drafts.csswg.org/css-syntax-3/#consume-escaped-code-point), [ident sequences](https://drafts.csswg.org/css-syntax-3/#consume-name), [declarations](https://drafts.csswg.org/css-syntax-3/#consume-declaration), and [substitution](https://drafts.csswg.org/css-values-5/#substitution). Primary snapshots/FETCH records are retained from the immediately preceding review; the relevant algorithms were freshly read again for this diagnosis.

## Exact source chain

Searchfox discovery is retained; exact local tokenizer.rs and custom_properties.rs are retained separately. consume_name→consume_escape consumes the escaped space as identifier content. VariableValue::parse then runs byte-based trim_ascii_end over the stored slice. For bytes x/backslash/space this deletes the last byte, storing x/backslash; reparsing that incomplete escape produces U+FFFD. The same trim appears in before-trailing-fix-custom-properties.rs. No browser on that older binary was run: preexistence is source-derived. Last-token metadata stays Ident either way, so the preceding metadata-only repair does not address this loss.

## Runtime and controls

One fresh-profile existing-binary run, complete and source/binary/fixture-stable: **4 discrepant states, 20 passing states**. Both escaped-space forms (with/without extra outer whitespace) fail on initial setting and re-setting; restoration to ordinary values passes. Literal controls compute escaped x-space while substitution computes x followed by U+FFFD. Specified and computed custom-property CSS already lack the escaped space. Hexadecimal-space escape, comment shielding, quoted trailing space, and ordinary identifier controls pass. CSS.supports accepts every literal. No animation/keyframes are running: animation-name is only a convenient identifier observer.

runtime-v1/raw.json retains every observation; RUN.json binds the command, source, binary, script and fixture before/after. The sandboxed attempt could not bind localhost and launched no browser; the authorized escalated attempt completed. The owned browser was terminated after callback and its profile removed with exact byte inventory in CLEANUP.json. No native source, production WPT, Git or build changes occurred.

## Proposed next step

escaped-trailing-space.html is an **unexecuted six-test WPT proposal**, derived from the executed 24-state diagnostic. Root owns installation and harness execution. A repair should trim only the actual outer whitespace-token suffix while preserving bytes consumed as part of a token, including escaped/hex whitespace. Tracking the end position of the last non-whitespace outer token is a candidate design, but nested parser positions, comments, EOF-generated closers, reference offsets and fallback slices require review before implementation. A check of only the final token kind is insufficient for an escaped-space token followed by real whitespace. No novelty claim or broader escape correctness claim.

## Review of proposed scanner-length approach

Returning trailing_whitespace_len from the last outer WhiteSpace payload is simpler than a new position accumulator. Exact consume_whitespace returns parser.slice_from(start_position), so its payload is the original raw byte slice. CRLF still counts two bytes despite newline bookkeeping; there is no decoded-whitespace length mismatch. Reset the length to zero on every other outer token, and do not propagate nested lengths. An EOF-repaired unclosed token has an outer non-whitespace class and zero trim length. Fallback slices should ignore this new result and preserve their whitespace. For old standalone trim_ascii_start code, saturating subtraction accommodates the all-whitespace overlap; current token-skipping code does not require that overlap allowance. This is a source review of the proposed algorithm, not a review of a yet-written patch.

Residual preexisting distinction: a backslash delimiter followed by newline requires the newline when serialized; removing that whitespace token can change the next parse to an escaped EOF. CSS Syntax serialization explicitly treats this delimiter specially. The proposed length tracking fixes escaped token content loss but does not by itself establish universal token round-trip preservation. That additional source-derived case has not been run here and remains a separate control/lead.
