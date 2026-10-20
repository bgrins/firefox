# parse_until_after: bounded source audit

## Finding

No new native defect established. The next useful component is an ownership-preserving delimiter continuation over the accepted `NestedControl.untilBefore` and raw block-recovery model. The additional proof should establish the direct ASCII advance and curly-recovery boundary; it must not simply assume a valid final cursor or annotation trace.

This audit performed read-only source/spec inspection. No compiler, browser, live test, production edit or Git mutation was performed.

## Sources and discovery

Searchfox found two definitions and five production calls, all in cssparser, plus one direct unit-test call. No direct Stylo `parse_until_after` call was found in the restricted servo query. The method wrapper always chooses Consume; the free-function Stop variant is used by declaration-versus-nested-rule parsing. Searchfox file retrieval initially hit sandbox DNS failures and succeeded with read-only network escalation. This CLI version lacks `--permalink`; no fabricated revision URL is used.

Exact current `parser.rs`, `rules_and_declarations.rs`, and `tokenizer.rs` snapshots are retained. The rules file equals the retrieved upstream file. Local parser differs only by the accepted depth-limit cleanup. Local tokenizer includes three separately accepted changes in dashed-escape lookahead, long-number conversion, and bad-URL recovery. None changes the reviewed direct `advance`, punctuation classification, or delimiter-set providers. The current parser/tokenizer match the accepted nested-control predecessor snapshots; SOURCE-IDENTITIES.json checks this relation.

Current primary baseline: CSS Syntax3 ED16 October2026, retrieved19 October2026, https://drafts.csswg.org/css-syntax-3/. Relevant anchors: #consume-a-declaration, #consume-a-qualified-rule, #consume-a-blocks-contents, #consume-simple-block. Declaration recovery ends at the next top-level semicolon while leaving an enclosing closing brace to its owner; component blocks consume their matching close while treating mismatched closers as contents. These rules motivate the ownership split but do not by themselves prove every caller's grammar. Full retained source bytes and hashes make the normative baseline explicit.

## Caller map

| Caller | Requested stops | Error policy and ownership |
|---|---|---|
| `RuleBodyParser::next`, identifier/declaration arm | Semicolon | Stop when qualified rules are allowed, then reset to declaration start before qualified-rule retry; otherwise Consume. |
| `RuleBodyParser::next`, nondeclaration/nonqualified arm | Semicolon | Consume with callback error, preserving enclosing block close. |
| `StyleSheetParser::next`, first `@charset` | Semicolon or opening curly | Consume entire discarded statement/block; subsequent rule remains available. |
| `parse_qualified_rule`, custom-property-shaped prelude | Semicolon when nested, opening curly when top-level | Consume recovery boundary, then return invalid-rule error. |

`parse_at_rule` itself uses until-before and explicit next/nested dispatch, so its semantics should not be silently folded into the until-after theorem. The direct existing `line_delimited` test covers entering with a pending curly block, failed entire callback, recovery to an outer semicolon, and leaving a following comma. It does not explicitly test overlapping stop ownership, cached delimiters, annotation effects, or Stop-error early return.

## Source control flow and rejected leads

1. `parse_until_before` temporarily installs the union of old and requested masks, runs the callback with exhaustion checking, and restores the old mask. On Stop/error it returns immediately. `parse_until_after` repeats that guard, so an early callback error cannot consume a delimiter or force pending-block recovery.
2. In all other branches, until-before first clears any pending opener through block recovery and drains to EOF or a union delimiter. The direct advance is therefore at a token boundary and has no pending opener. This conclusion needs the lexical progress/completion contract, not just a finite fuel parameter in a model.
3. At a boundary owned by the old mask, after leaves the byte untouched even if the requested mask also contains it. Otherwise the debug assertion requires requested ownership. Native public delimiter masks contain only ASCII punctuation. Advancing one byte cannot split UTF-8 or alter line counts on this branch.
4. Direct advance intentionally does not call tokenization and does not populate or clear cached_token. This is not identical to public next(). Its correctness requires a coherent cache and the punctuation provider law: these particular delimiter bytes cannot produce a substitution observation or a sourceURL/sourceMappingURL annotation. Old cached entries remain coherent because source bytes are immutable and position keys are retained.
5. The opening-curly branch consumes the opening byte, then calls full `consume_until_end_of_block(CurlyBracket)`. It need not manufacture a pending opener: the explicit stack argument owns that block. Recovery ignores outer stops inside it and updates observations/annotations through raw reads, while retaining the cache. Nested blocks and mismatched closes use the existing complete stack loop.
6. Annotation and observer changes inside skipped curly bodies are real and must not be erased by the reference semantics. Conversely, punctuation-only advance leaves them unchanged. Earlier cache-observer public-history findings are not new defects caused by until-after; no new ordinary stylesheet witness was established here.
7. An arbitrary callback can change the nested-block limit or observation mode. The helper does not promise to roll those changes back. The accepted represented-callback grammar and explicit caller reset behavior must remain admissions rather than become universal callback restoration claims.

The direct-byte branch therefore has a useful proof obligation but no demonstrated missing token, wrong next declaration, or observable CSS mismatch in the inspected production uses.

## Next component and limits

CONTRACT.md specifies the proposed independent boundary relation and discriminating cases. It reuses the already accepted predecessor rather than re-proving observation histories under new names. Complete grammar correctness, arbitrary callback effects, native UTF-8/codec/machine bounds and browser-level declaration recovery remain outside the proposed theorem unless separately connected. The queued bug86 formal review takes priority over implementing this component.
