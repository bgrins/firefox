# Parser depth-limit declaration recovery: independent adjudication

**Confirmed recovery defect; approve the proposed one-line source repair for candidate browser validation.** No blocking native concern found. This is not final landing approval: the producer's universal proof and the candidate Gecko/browser pair remain separate gates. Review date: 2026-10-19. No novelty claim is made.

## Independent normative trace

Scenario: an ordinary element's `style.cssText` is assigned `color:red;padding-left:` followed by 76 nested `calc(` functions, `1px`, 75 closing parentheses, then `;color:blue;)`. There is no important declaration, substitution function, animation, inheritance-dependent expected color, or valid deep calculation whose support is being demanded.

1. CSSOM's [cssText setter](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-csstext) parses a CSS declaration block and installs its resulting declarations. [Parse a CSS declaration block](https://drafts.csswg.org/cssom/#parse-a-css-declaration-block) calls CSS Syntax's declaration-list parser, then processes each returned declaration under its property's rules.
2. [Parse a list of declarations](https://drafts.csswg.org/css-syntax-3/#parse-a-list-of-declarations) invokes declaration consumption for the initial `color` and the following `padding-left`.
3. [Consume a declaration](https://drafts.csswg.org/css-syntax-3/#consume-a-declaration) obtains a component-value list with semicolon as its stop token. [Consume a component value](https://drafts.csswg.org/css-syntax-3/#consume-a-component-value) delegates each function to function consumption.
4. [Consume a function](https://drafts.csswg.org/css-syntax-3/#consume-a-function) recursively consumes its component values through the matching closer or EOF. Thus the semicolon and `color:blue` remain inside the outermost function. The invalid padding value cannot publish another declaration. The independent checker's simple balanced-parenthesis oracle finds exactly two top-level declarations in every generated witness.
5. [CSS Values 4 math syntax](https://drafts.csswg.org/css-values-4/#calc-syntax) requires support for at least 32 levels, and says excess over the supported nesting must be treated as invalid. Firefox may reject depth 76. That permission does not transform nested content into declaration-list input.
6. [CSS Syntax error handling](https://drafts.csswg.org/css-syntax-3/#tokenizing-and-parsing) permits aborting processing at an unhandled parse error. Such an abort does not explain accepting a newly exposed blue declaration. The preceding red declaration is the test's reference; this review does not demand that an unsupported calculation compute successfully.

**Verdict: REACHED** — ordinary declaration parsing must retain the function's delimiter ownership; blue is not a declaration in this input. The observed blue result is a recovery defect, independent of the chosen nesting limit. This is a manually inspected current-primary-spec chain, not an exhaustive tool-generated graph proof. `webspec-index` is still missing after the earlier root bootstrap; no unauthorized Mach bootstrap was performed. Current primary excerpts, including the explicit UA-limit paragraph, are retained. No invented step quotations or unverified graph-completeness claim is used.

Rejected alternatives: valid-deep-math support is irrelevant because the outer calc is already invalid; whole-input abort cannot synthesize blue; stylesheet qualified-rule retry and width's local rollback explain passing controls rather than disprove the inline padding path. A future WPT should preserve the preceding-declaration witness so the central assertion does not depend on arbitrary deep-value support.

## Source chain and cause

The full scout input manifest (175 files) was authenticated against root-supplied external pins before compiling source. I inspected the complete `parse_nested_block`, `parse_until_before`, `parse_until_after`, iterative block consumer, token/cache dispatch, declaration iterator, and participating Servo error paths. The original parser bytes equal root's successful Searchfox source retrieval. My own Searchfox CLI discovery was attempted but failed DNS; its attempted unsupported `--permalink` flag and retry error are retained honestly, not passed off as successful discovery.

`PropertyDeclarationParser` enables declarations and disables qualified-rule retry. Its value callback delegates to `DeclarationParserState::parse_value`, whose bang-delimited property parse inherits the outer semicolon boundary. The padding-left declaration table selects `NonNegativeLengthPercentage`; its mapped length-percentage parser enters `CalcNode::parse_length_or_percentage` and `CalcNode::parse`. Recursive `parse_one` calc handling re-enters the same nested parser. The first operand in `parse_product`/`parse_argument` propagates rejection rather than rolling the complete value back. Afterward the noncustom-property helper scans for substitution functions, but cannot cross the prematurely exposed semicolon and has seen none. The error returns without resetting the initial declaration position. Declaration cleanup then accepts the leaked blue declaration.

At the rejection site, `state.take_at_start_of()` already cleared the pending child block. The depth guard returns without consuming it. The enclosing cleanup starts its iterative stack with the parent only, mistakes the child's closer for the parent's, and eventually exposes one formerly nested semicolon. The ordinary non-limit cleanup already consumes both pending nested blocks and the current block.

The width control rolls back its length attempt through `try_parse`. Stylesheet `NestedRuleParser` enables qualified retry, and `RuleBodyParser` restores the start before retrying. Both mask this failure. Generated longhand code and the entire DOM/cascade are not compiled in the reduced native witness; pinned dispatch source plus root's actual browser reproduction supply that bridge. This review does not claim all parser consumers are audited.

## Proposed repair and risk assessment

The sole source change calls `parser.consume_until_end_of_block(block_type)` in the existing depth-limit rejection branch, before returning the same `TooManyNestedBlocks` error. The checker reconstructs the whole candidate from the original by exactly this insertion.

This discharges the block obligation just removed from `at_start_of`. It does not increment depth, replace the enclosing stop delimiter, invoke the rejected callback, raise the nesting limit, or introduce recursive cleanup. The existing iterative helper tracks the exact block type; mismatched closers do not close another type. It reads complete tokenizer tokens, so delimiters in strings/comments remain inert. It deliberately ignores the enclosing semicolon stop until it has consumed this block or EOF. Subsequent parent cleanup then starts at the correct position.

The helper uses a `SmallVec` for additional lexical nesting and retains its existing allocation behavior. The repair preserves the call-stack protection, but is not a no-allocation or heap-exhaustion proof. Cache/observer behavior is that of the existing iterative tokenizer cleanup, not an attempted repair of the scout's separate observer-history leads. There is no performance measurement claim. Delaying the pending-block take could repair some parent unwinds, but would expose a different direct error-return cursor; the chosen eager cleanup matches ordinary nested-call completion more closely.

## Independent native challenge

A fresh artifact-only build compiles the full pinned cssparser crate and its Rust dependencies for original and candidate. The driver is independently written and does not reuse the producer's expected rows or final-state providers. Both variants complete **126 cases**:

- 90 unwind cases: limits 0/1/2/3/75, depths 1/2/3/4/74/75/76/77/100, with/without a rollback wrapper. The raw source intentionally places blue inside the last function and green outside it. Original exposes blue in 24; candidate exposes it in zero. Limit zero and rollback controls remain correct.
- 30 caught-error cases: parenthesis/square/curly children, empty body, semicolon, quoted/comment delimiters, wrong-type closers, and nested mixed blocks; each runs fresh and with a primed/reset cached opening token. The rejected callback must not execute and the exact error must be `TooManyNestedBlocks`. Original misses the following in-parent marker in all 30; candidate reaches it in all 30.
- Six EOF cases: all three block types, fresh/cache-prime variants. Candidate reaches physical EOF after rejection; original does not. A subsequent separate root block in the caught-error cases successfully invokes its callback, checking that active depth and outer semicolon handling remain usable.

The 252 total executions are finite public-API checks, not a universal native theorem. No native private field is supplied as expected output. Early driver development had a compile-time borrowed-string comparison error and a mistaken use of `slice_from` as remaining input; both were corrected before the retained final source/receipts. Neither was a production finding. The final source-only replay passes without warnings/errors in the witness; a fresh manifest-authenticated replay also rebuilt both variants successfully.

## Browser adjudication, tests and prior art

The retained baseline raw JSONL has exactly 20 named subtests plus two OK harness records. The sole failure is inline padding-left at depth 76, reporting blue instead of red. Nine other padding cases and all ten width cases pass. All names/statuses match independently generated expectations; raw/console hashes and before/after pins are checked, including exact parser and probe bytes. This is root-executed local shared-tree evidence; I ran no browser or Gecko build.

Existing cssparser `nested_block_limit` tests exercise 75/76/10000 and configurable/disabled limits, but do not inspect declaration visibility or the direct post-error cursor. `outer_block_end_consumed` covers earlier issue 71's normal cleanup path. Those tests should remain regression gates, along with the new inline witness, rollback/stylesheet controls, and a genuinely external following-declaration control. The independent native suite adds mixed delimiters, EOF, cached opener and caught-error state checks that the initial browser pair lacks.

Bug 1973126 and its duplicate stack-overflow report explain why the depth limit must remain. The retained bounded issue search found related cleanup/stack-limit history, not evidence establishing this report's novelty. It is not an exhaustive Bugzilla/GitHub search. The separate token-observer/source-map histories are explicitly excluded from this repair and acceptance.

## Handoff and replay

The defect and one-line repair are supported by current normative analysis, exact source inspection, finite independent native execution, and browser baseline reproduction. Remaining: candidate Gecko build/WPT pair, minimal standalone native+WPT package, and independent review of the producer's eventual universal model/source bridge. The producer's unsealed Lean progress is not counted as accepted formal verification here.

After authenticating this artifact's manifest/checker using the external handoff pins:

```
python3 -I -S -B artifacts/css-parser-depth-recovery-independent-v1/check.py --manifest <sha256>
python3 -I -S -B artifacts/css-parser-depth-recovery-independent-v1/check.py --manifest <sha256> --native-output /absolute/new/output/path
```

The latter rebuilds only artifact-local Rust programs using the pinned compiler. Commit the manifest-listed inputs plus `MANIFEST.json` and `FREEZE.json`; omit every unlisted development/replay directory and binary. Python, compiler and standard-library installations remain trusted tools. No universal machine-memory or full CSS conformance theorem is asserted.
