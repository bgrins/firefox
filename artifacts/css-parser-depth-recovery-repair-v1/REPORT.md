# Depth-limit recovery proposal

## Repair

Call the existing iterative `consume_until_end_of_block(block_type)` before returning `TooManyNestedBlocks`. `parse_nested_block` already took the pending opener. Without this cleanup, parent error recovery consumes the child's closer as its own, allowing text still inside a function to become a declaration.

The proposal preserves the 75-level default limit, the error kind and ordinary parsing. It does not raise limits or recurse to skip rejected contents. Direct catch-and-continue callers now receive the same matching-block cursor normalization as ordinary nested parse errors. Closing tokens of another kind remain internal; EOF consumes the remainder. The exact patch is `native.patch`, against the original parser retained from the sealed public-stream scout. It has no dependency on the quote-recovery or other custom-property repairs.

## Oracle and observed evidence

CSS Syntax [consume function](https://drafts.csswg.org/css-syntax-3/#consume-a-function), [consume component value](https://drafts.csswg.org/css-syntax-3/#consume-a-component-value) and [consume declaration](https://drafts.csswg.org/css-syntax-3/#consume-a-declaration) keep an inner semicolon inside its function. A resource rejection can invalidate or stop processing the declaration; it cannot publish the nested `color:blue`. The baseline is an earlier explicit red declaration. Supporting a valid expression at depth76 is not assumed.

Root reported one browser failure for inline padding-left at depth76, with the other nine padding cases and ten width controls passing, in `css-parser-depth-recovery-browser-v1/baseline-result.json`. This producer did not run a browser. Width uses a rollback wrapper and stylesheet parsing retries qualified rules, both masking controls. Relevant prior work includes bug 1973126's nesting limit and closed rust-cssparser issue71's non-limit outer-block cleanup. No novelty claim is made.

The frozen scout's full current source and spec captures are retained. The new native matrix is fixed at24 observations per variant: actual declaration-iterator controls, public cache/observer controls, default-limit recovery, caught errors for paren/square/curly/EOF, successful subsequent depth use and disabled-limit nested parsing. Candidate fixes the source-level recovery differences; unrelated observer discrepancies remain. Two compiled native mutants omit cleanup or use the wrong closing kind. Both must fail their candidate assertions.

## Formal component

`lean/Recovery.lean` models the actual iterative stack and an independent tree-shaped grammar for bodies and unfinished EOF content. Universal results connect grammar to exact cleanup suffix, prove cleanup progress and suffix bounds for arbitrary finite tokens, compose child rejection with parent cleanup, preserve pending/depth/limit/stop state and retain limit0 behavior. Closed witnesses distinguish original and repaired publication. Two semantic Lean mutants remove cleanup or pop a mismatched closer; the same theorem source must reject them.

See SOURCE-BINDING.md for the exact mapping and unproved boundaries. This is a substantive recovery component, not a claim of full native parser verification. Byte-to-token decoding, packed metadata, allocation and compiler semantics remain premises. Full Gecko callback/generated-property execution is runtime evidence supplied separately by root.

## Integration and remaining gates

Root owns production integration, vendor checksum, Firefox compilation, browser pairing, lint and commit. The proposed WPT copy is still producer-unexecuted; root may refine its final test independently. Before accepting a production patch, bind its final parser bytes to this exact candidate (formatting changes require an addendum), pair the browser failure/controls and retain existing nesting-limit tests. The independent reviewer owns its separate126-case source challenge; it is not counted as this capsule's result.
