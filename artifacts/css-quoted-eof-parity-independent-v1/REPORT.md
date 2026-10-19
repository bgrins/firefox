# Independent parity repair review

**Recommendation: source/proof proposal approved for root integration and browser validation. Native acceptance remains open.** The patch repairs even terminal backslash runs without taking credit for the separate endpoint or escaped-quote repairs.

I authenticated all 180 inputs against the supplied freeze/manifest/checker pins before executing helpers. I read both complete Lean modules, native extraction/driver/facades, source deltas, complete relevant parser/tokenizer methods, browser oracle, retained prior-issue evidence and checker. The fresh relocated source-only replay passed 20 exact theorem audits and all standalone, endpoint and combined native configurations. The review checker independently enumerates theorem names and verifies every retained native result family.

## Source and semantics

The standalone patch replaces only the late-pop `ends_with` predicate with odd maximal trailing-backslash count. An even run is a sequence of escaped backslashes and must remain intact; an odd run ends in the backslash ignored at EOF. The existing missing-quote suffix guard limits the edit to the same recovery path. Normal quoted strings, zero runs and non-string EOF recovery are unaffected. This follows the string algorithm's escape and EOF cases. [CSS Syntax string consumption](https://drafts.csswg.org/css-syntax-3/#consume-string-token).

The native reverse byte iterator stops at the first non-backslash, so it cannot mistake a UTF-8 continuation byte for ASCII backslash. The count is bounded by the source length; its parity test introduces no subtraction. The subsequent pop occurs only for a positive odd run. It adds at most one reverse scan of the terminal run, on this exceptional recovery path, without allocation. No benchmark claim is made.

After the endpoint patch, this decision must be recorded before endpoints are constructed. The supplied integration patch correctly strengthens `removed_backslash` at its single recording site. Both the endpoint subtraction and final pop then use that same flag; even runs perform neither edit. This is an interface/composition review of the new parity change, not an independent acceptance of my own endpoint implementation. The endpoint repair has a separate reviewer.

The standalone source intentionally still has the odd-backslash endpoint defect. It is independently applicable as a semantic patch, but the root's branch should use the endpoint-based adaptation. The quote-closure predicate is untouched. The two semantic adaptations commute byte-for-byte on the retained formatted endpoint source, and both packages retain the same combined source.

## Proof and oracle

`TerminalString.consume` is a front-consuming pairwise escape reference. `ParityRepair.remove` uses trailing-count parity. The proofs derive retained even run length, decoded preservation, closure before arbitrary appended suffix, ordinary-prefix framing, safe deletion count and endpoint-length alignment. They are not defined by assuming the desired trace equality. The 20 audited names exactly match the declarations; only standard Lean axioms appear.

Admission still requires tokenizer state inside the correct string immediately before its maximal terminal slash run. The `other` grammar is restricted ordinary content; it does not model hex escapes, NUL, preprocessing or arbitrary prefix decoding. The `trailing_run` lemma operates on a supplied reversed-run decomposition; actual Rust `.bytes().rev().take_while()` correspondence is source reasoning, not a verified lowering. UTF-8, usize, metadata normal completion, allocation and compiler/library semantics remain external. This is a useful terminal-run theorem, not whole CSS string parsing.

The independent reviewer decoder consumes raw ASCII escape pairs from the front and matches all 22 fixture expectations, without using the repair's deletion predicate. The actual native driver checks decoded tokenizer content, then parses recovered CSS plus `, serif`, asserting content preservation and exact unconsumed suffix. The baseline browser's valid literal comparison uses the same normative value distinction, without requiring a raw quote spelling. Native opening-only controls differ from the browser's two final fallback controls, as the producer correctly states.

Original native rows have eight semantic failures. Parity alone removes its four even-positive-run failures and retains all four escaped-terminal-quote failures, in both standalone and endpoint modes. Combined source has 22 passing rows. Each native mutant is compiled: restoration returns baseline failures, while never deleting breaks the two one-backslash controls. In combined mode, restoration uses the endpoint baseline and therefore removes both semantic repairs; it is not a selective parity-only mutation there. The standalone/endpoint mutants provide the isolated discrimination.

The two Lean mutation files are deliberately false counterexample assertions rejected by `decide`; they do not mutate and recompile all theorem definitions. This is narrower than an unchanged-theorem-suite mutation test. The native mutation gate independently changes the actual extracted source. No stronger coverage is inferred.

## Remaining gates

Root must bind final formatted source, run the candidate Gecko build and paired browser tests, and package the minimal native+WPT commit. For independent landing, select these four failing semantic cases plus shared passing controls; the other repair's four remaining failures must not be included as newly passing expectations until it lands. Preserve all 22 as composition evidence. The full tokenizer, provider lookup, cascade, recursive-offset proof and memory/metadata admissions remain separate open work. No browser candidate success or novelty claim is made by this report.
