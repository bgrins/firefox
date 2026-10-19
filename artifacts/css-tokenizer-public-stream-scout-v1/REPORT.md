# Public parser state and recovery scout

## Status

Source-only counterexamples, not browser-confirmed defects or universal proofs. The exact current cssparser source is compiled with pinned Rust dependencies. No Firefox build, browser, native edit, WPT installation or Git operation was performed. The two proposed browser files are **UNEXECUTED**. Root owns runtime adjudication.

## 1. Priority: depth rejection loses a pending block

`parse_nested_block` takes and clears `state.at_start_of` before checking `nested_block_limit`. At the default limit (75), it returns `TooManyNestedBlocks` without consuming the rejected block or retaining its pending obligation. The enclosing call runs its normal cleanup from inside that child. Its `consume_until_end_of_block` stack starts with only the enclosing block, so the child's closer terminates that cleanup prematurely. Repeated unwinding loses one level. An inner semicolon can consequently become visible to declaration recovery.

The exact native witness parses `calc(` repeated N times, `1px`, N−1 closing parentheses, then `; color:blue; ); color:green;`. All values are invalid; the question is recovery extent. At N=1,74,75 the next declaration is green. At N=76,77 it is blue, even though blue is text inside the outermost function. No support for a valid deep math expression is assumed.

The additional witness uses unchanged `RuleBodyParser` and its real `parse_until_after` control flow. With declaration parsing enabled and qualified-rule retry disabled, N=76 accepts both red and blue; N=1,75 accept only red. Enabling qualified retry accepts only red at all three depths. The property callback is a reduced recursive calc parser, not an extracted Gecko math implementation. The complete iterator and tokenizer are actual compiled source. This is a source-level counterexample with a manually reviewed Firefox caller bridge.

### Firefox reachability and rollback controls

`PropertyDeclarationParser` implements `parse_declarations=true`, `parse_qualified=false`. Its value handler invokes `DeclarationParserState::parse_value`, which calls `parse_until_before(Bang, PropertyDeclaration::parse_into)`. This retains the enclosing semicolon stop. `PropertyDeclaration::parse_into` dispatches the padding-left longhand to `NonNegativeLengthPercentage`; the retained longhands table declares that type and quirks parsing.

`NonNegativeLengthPercentage::parse_quirky` directly maps `LengthPercentage::parse_non_negative_quirky`, which enters `parse_internal`. A Function goes through `CalcNode::math_function` and `parse_length_or_percentage` to `CalcNode::parse`. Each nested calc in `parse_one` calls that same parser. Its `parse_argument` / `parse_product` first-child errors propagate. The depth rejection therefore unwinds through actual nested-block cleanup. The noncustom property helper's subsequent substitution-function search cannot pass the prematurely exposed semicolon and has seen no var/env/attr. The error reaches declaration recovery without an initial-position reset.

Two important controls prevent overgeneralization. `NestedRuleParser` enables qualified-rule retry, and `RuleBodyParser` resets to the declaration start before that retry. Separately, width's `Size::parse_quirky_internal` uses `try_parse` around its length attempt, restoring position on failure. These can mask the lost obligation. The original width probe is retained; the **padding-left** probe is the primary browser candidate. Generated longhand code and the full DOM/cssText implementation are not compiled here; source dispatch and normal platform entry remain browser-admission obligations.

### Independent normative oracle

CSS Syntax's [consume declaration](https://drafts.csswg.org/css-syntax-3/#consume-a-declaration) obtains component values; [consume component value](https://drafts.csswg.org/css-syntax-3/#consume-a-component-value) treats a function as a unit; [consume function](https://drafts.csswg.org/css-syntax-3/#consume-a-function) includes its contents through its matching closer. An inner semicolon cannot create an outer declaration. The earlier red declaration remains the expected result, whether the invalid padding declaration is ignored or error processing aborts there. This oracle does not prescribe implementation resource limits. CSS Syntax permits stopping at a parse error, but exposing an inner declaration is neither such a stop nor specified recovery.

`depth-limit-padding-recovery.html` has inline and stylesheet cases at depths 1/74/75/76, plus genuinely external blue-declaration controls. Every nested-value case expects red. The reference base is the preceding explicit color declaration; no layout measurement, font, inheritance or arbitrary depth-support assumption is involved. The width version is a masking control. Node syntax checks are not browser results.

### Narrow repair direction

Keep the limit and error kind. On the limit branch, consume the rejected block with the existing iterative `consume_until_end_of_block(block_type)` before returning. This preserves the normal public nested-parser cleanup contract and does not add recursive calls or increment/decrement depth. The helper deliberately ignores `stop_before`, so inner delimiters remain internal. Audit cache position and comment/function observer effects exactly as in ordinary cleanup. An alternative that delays taking the pending flag can repair caller cleanup, but leaves the direct error-return cursor less completely normalized; do not assume the alternatives have identical API behavior. Neither proposal is implemented or validated here.

## 2. Cached Function omits newly enabled observer

Prime Function(var) while tracking is off, reset to its start, enable tracking, and read it again. The public API returns the cached Function while `seen_arbitrary_substitution_functions` reports false; a fresh read reports true. The cache hit assigns end-state without repeating `see_function`. This violates the natural public 'seen since enabled' reading, but no Firefox browser defect is established. The usual noncustom property helper enables tracking before its first token, and geckolib's substitution helper creates a fresh parser and enables tracking before parsing. Neither supplies the bad history. Tracking before the first read and then resetting correctly retains true; speculative persistence is useful and is not itself a bug.

## 3. Comment replay changes final metadata

For `(/*# sourceURL=A */)/*# sourceURL=B */`, save state just after the opener. First reading the outer comment skips the block and ends with B. Resetting there and reading again retokenizes the inner A but returns cached B without replaying its observer effect; the final URL is A at EOF. A fresh parse ends with B. `sourceMappingURL` behaves identically. This is a reproducible API history, not an established CSSOM/tooling regression. `Stylesheet::parse_rules` reads both final fields, and StyleSheet exposes them (with source-map header precedence), but no concrete stylesheet parser path reproducing this cache history is shown. CSS Syntax does not specify observer rollback. The modern source-map extraction contract and tooling expectations must be joined to an actual caller before labeling this a browser bug.

## Prior art and coverage

Primary retrievals and dates are retained under spec/. They are parsed web responses, not authenticated raw HTML or a claim that fragment IDs were checked. Bug 1973126 added a CSS nesting limit to prevent stack overflows and is relevant provenance. Its related stack-overflow reports are not this recovery witness. Closed rust-cssparser issue 71 concerns an outer closer left behind when an inner function was not consumed; the existing `outer_block_end_consumed` test covers that earlier non-limit path. Existing `nested_block_limit` tests check success/error at 75/76/10000, not declaration visibility after rejection. No novelty claim is made. WPT/metadata discovery is bounded and absence is not execution evidence.

Inspected: complete parser iteration/reset/nested/until/block-consumption providers; declaration iterator; relevant complete Servo property/calc/declaration/stylesheet callers; final metadata publication/getters; existing parser and source-map tests. Not closed: all parser consumers, generated longhand code, actual DOM/cssText execution, selector/style-rule retry equivalence, metadata tooling after arbitrary speculative histories, allocation failure and machine-level memory correctness.

## Ranked next formal contracts

1. **Error cleanup preserves delimiter ownership.** Derive an independent stack of lexical block obligations from token prefixes; prove successful and rejected nested calls consume exactly their own matching closer or EOF, restore enclosing stop/depth, and cannot publish inner declaration boundaries. Include limit0, mismatched closers, cache hits, caller abort/retry and fallible allocation premises. The current limit branch falsifies the unconditional contract.
2. **Public token/observer refinement.** Separate lexical token identity and cursor state from observer effects. Specify when enabling tracking starts a new epoch and derive cache-hit behavior, rather than assuming physical tokenization equals logical observation. Current priming history is a concrete failed premise.
3. **Metadata publication under permitted parser histories.** Define final source-map annotation selection independently, prove only the actual admitted caller histories, and retain speculative persistence where intentional. The replay example rules out an unrestricted final-state equivalence theorem; actual Firefox reachability remains open.

These are substantive future targets. This scout does not add a Lean theorem count or claim full tokenizer/parser verification.
