# Native and WPT review

## Actual failure

The raw typed-attribute path constructs a fresh Parser from the untrimmed attribute and calls VariableValue::parse. The original constructor records offsets against the current position, then removes leading bytes from stored css with trim_ascii_start without rebasing the recorded references. For ` var(--v)`, the reference is [1,9) while stored `var(--v)` is eight bytes. Substitution advances its source cursor to 9 and the suffix slice fails bounds checking. Retained release extras identify the content-process panic at exactly that index; a missing callback alone is not used to diagnose a crash.

CSS Values 5 attr substitution first substitutes functions in a typed attribute value, then parses the result against its syntax. The fixture's ordinary whitespace-prefixed var resolves to a valid 37px length. VT and NBSP are not CSS whitespace; their values fail this length grammar and select the distinct 19px fallback. The retained primary HTML excerpt and source digest identify the reviewed normative basis.

## Prefix and offsets

The candidate consumes one initial Token::WhiteSpace before capturing input_start. The tokenizer's whitespace token covers the maximal contiguous run of TAB, LF, FF, CR and SPACE, retaining the original byte extent of CRLF. It does not treat VT or NBSP as whitespace. Non-whitespace lookahead restores the saved ParserState, so comments remain in the stored slice. Unlike skip_whitespace, this step does not discard a leading comment or whitespace following that comment.

Removing post-scan trim_ascii_start makes the stored slice and every recursive reference use the same origin. If the original position is a and the removed prefix length is k, both storage and range calculation now begin at a+k; a token at t is recorded at t-(a+k). Nested fallback parsing shares input_start, so no separate nested rebasing is required. This repairs the concrete prefix-coordinate mismatch. Existing closure repair, trailing trim, UTF-8 boundary and recursive endpoint machinery is unchanged and is not universally re-proved by this review.

First-token metadata now describes the retained stream instead of discarded leading whitespace. The empty-whitespace case likewise starts with Nothing. This is consistent with the normalized stored value; the review does not require metadata to remain byte-identical to the inconsistent original constructor.

## Lookahead and observer effects

The added next call neither enables nor queries tracking and does not replace the name list. ParserState reset does not undo tracker/cache/annotation effects. For an eligible first non-whitespace token, the fresh token observation is simply performed by the lookahead; after reset the scanner reuses the cache, retaining the observation rather than dropping it or requiring a second observation. A leading comment directive is similarly published on the first read and retained through cached replay. Existing relevant-cache late-enable limitations are neither introduced nor solved here.

This is not a claim that every parser field is unchanged. In a fresh attribute string beginning with Bang or semicolon, lookahead can populate a non-relevant delimiter cache before parse_declaration_value installs its additional stop boundary. That is not a tracked-function or annotation change. The next bounded parse still stops before the delimiter. Normalization also deliberately advances the parser before origin capture for whitespace.

The inspected real constructor entries are fresh parsers, normalized declaration starts, or nested callback starts after the opener has been taken. No caller was found intentionally entering VariableValue::parse with an unrelated pending opener. Arbitrary inconsistent parser states, cross-parser saved states, panic/allocator behavior and a universal parser-state bisimulation are outside this acceptance. Existing actual parser source and the accepted wrapper component support the stated cache/reset mechanics.

## Test design

The 26-case WPT tests the raw-attribute constructor, not a declaration path that already skips whitespace. Each case creates and cleans up a new element. A 37px success oracle is distinguishable from the 19px fallback. It covers all five whitespace bytes, CRLF, a mixed prefix, nested calc and nested fallback references, multiple references, escaped function spelling, multibyte comments, chained attributes, and plain/literal/trailing/comment/VT/NBSP controls.

The computed-width checks demonstrate substitution and safe execution. They do not directly assert internal reference ranges, retained comment bytes, token-serialization metadata or tracker state. Those properties are supported here by source inspection and belong in the separate extracted/formal constructor work if a stronger claim is desired. No extra browser test is required merely to duplicate those internal contracts.

The new WPT was run on the candidate only. Separate baseline and installed-release probes establish plain success and the whitespace crash. It would be inaccurate to call all 26 cases paired regressions.

## Upstream independence

Fresh Searchfox discovery finds the same trim-after-offset sequence and raw attribute entry upstream. The retrieved complete source is retained with a content hash; no commit identity is inferred from a tip fetch. The local constructor includes earlier removed_backslash plumbing that is absent from the retrieved upstream source. The two semantic edits apply independently: insert the whitespace-token step at entry and remove trim_ascii_start. The artifact-only upstream adaptation preserves all upstream EOF-repair code and other methods. No isolated upstream build/browser execution was performed, and current native.patch context should be regenerated against the desired base rather than making an unrelated EOF repair a prerequisite.
