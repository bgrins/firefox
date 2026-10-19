# Production tracking entry and wrapper source audit

## Result

No new production-reachable bug was established. The current discovered enable protocols exclude a relevant cached Function at entry: they supply either a cold parser or a successfully returned Colon, followed only by operations that preserve the cache. The original public late-enable and query/re-enable counterexamples remain valid and are retained, not declared unreachable for every library caller.

This is a static source admission proposal building on the accepted public-history component. No new theorem, browser observation or full generated-property-parser correctness claim is made. Its main additions are an explicit wrapper state/effect ledger, the nested-rule forwarding route, and a ranked composition contract for the actual declaration helper's multiple query branches.

## Discovery and source versions

Fresh whole-tree Searchfox queries find two production enable expressions: `parse_non_custom_property_declaration_value_into` in properties/mod.rs and `compute_arbritrary_substitution_functions` in geckolib/glue.rs. There are three query expressions in the declaration helper and one in the geckolib helper. The only other enable/query code hit is the cssparser test. The direct `PropertyDeclaration::parse_into` call inventory consists of parse_one_declaration_into, DeclarationParserState::parse_value and supports Declaration::eval. Exact commands/results are retained under discovery.

An initial sandbox request failed DNS; successful read-only escalated Searchfox requests are retained. `--get-file` retrieves GitHub main bytes. Those indexed/upstream snapshots are identified separately from locally changed source; they are not silently treated as exact current local files. Current parser, tokenizer, properties/mod.rs, declaration_block.rs and glue.rs are copied and hashed in SOURCE-PINS.json. Rules/declarations, supports and rule-parser snapshots are fetched discovery sources. The previous public-history capsule and relevant theorem/counterexample sources are authenticated against its manifest and retained under prior.

## Actual enable-entry protocols

| Route | Cache at enable | Source-derived argument |
|---|---|---|
| `parse_one_declaration_into` | Cold | Constructs Parser, reads only position/location, then parse_entirely invokes its closure before any exhaustion read. `PropertyDeclaration::parse_into` only skips whitespace before entering its noncustom helper. |
| `parse_property_declaration_list` → PropertyDeclarationParser → DeclarationParserState | Colon | RuleBodyParser consumes the property Ident, then its declaration callback successfully calls expect_colon immediately before parse_value. Property-ID/context work does not read the input. parse_until_before changes stop delimiters and invokes its closure before cleanup. |
| `NestedRuleParser::parse_nested` → RuleBodyParser → NestedRuleParser::parse_value → DeclarationParserState | Colon | The nested-rule forwarder reaches the same declaration parser state through RuleBodyParser's successful-colon gate. A failed declaration may reset and retry as a qualified rule; any later declaration-enable attempt must pass a new colon gate. |
| supports `Declaration::eval` | Colon in a fresh parser | Evaluation creates a new Parser from the stored declaration text, consumes the property Ident and Colon, then enters the same noncustom helper. Speculative supports-condition parsing is on another parser history, not reused for this enable. |
| `Servo_GetSubstitutedValue` / `Servo_GetComputationSteps` → compute_arbritrary_substitution_functions | Cold | The helper creates a Parser and immediately enables tracking before VariableValue::parse. It queries only after a successful parse, then drops the parser; failure also drops it. |

The production name list is fixed `var`, `env`, `attr` for each of these enables. Custom-property declarations take another branch of PropertyDeclaration::parse_into and do not themselves enable tracking. Consuming a Colon need not be a cache miss: successful cached Colon also establishes a non-relevant cache. The accepted PublicEntry.returned_cache/colon_entry theorem supplies exactly this fact for primary fetch, pending the next()/expect_colon wrapper join.

### Why skipping before enable does not spoil the cache condition

`PropertyDeclaration::parse_into` calls skip_whitespace, saves state, then invokes the helper for noncustom properties. skip_whitespace first skips a pending block; afterwards it advances whitespace or consumes comments directly. Neither phase replaces cached_token. Therefore the cold/Colon cache condition survives even if raw observer effects occur. On these specific entry routes pending is also absent, since construction/Colon does not open a block. The property-context wrapper has no token read before calling the helper. No relevant Function is pre-read by this entry sequence.

### The helper is not one indefinitely enabled epoch

1. Enable, read the first token, and optionally test a CSS-wide keyword with expect_exhausted. A complete wide keyword queries/disables and returns.
2. Otherwise reset to saved value start without resetting cache or observer; parse the property with the existing generated parser.
3. On success, query/disables. If false, return the parsed value. If true, retain that Boolean, clear provisional declarations, reset and scan. On parse failure, no query has happened, so tracking remains active during the scan.
4. Scan via next() for substitution functions and top-level curly restrictions. Final `saved_seen || query()` is short-circuiting: a saved true skips the query, but already suffices. A false saved flag queries the still-active failed-parse epoch. Reject if no function or invalid curly shape; otherwise reset and parse VariableValue.

This branch structure never discards a true query result and then re-enables the same relevant cached token. Its proof needs both native mode and the local saved Boolean. After a successful query with true the later scan is intentionally untracked; claiming its native seen bit alone still equals all logical observations would be false. Early invalid-curly termination and deferred VariableValue parsing require their own validity result, not just an observer theorem.

## Wrapper effects and necessary composition

| Wrapper | Actual effects | Proof requirement |
|---|---|---|
| skip_whitespace | Pending raw block cleanup; raw whitespace/newline/comment consumption; comments update annotation fields; cache unchanged | Derive byte/cursor progress and logical comment writes, preserve cache coherence and epoch invariant, include pending Function observations. Do not model it as a pure cursor assignment. |
| next | skip_whitespace, then next_including_whitespace_and_comments | Join raw skip to primary fetch. Pending is clear after skip, so the primary pending phase is vacuous. Preserve current delimiter stop after skipping. |
| next_including_whitespace | Repeated primary fetch until token is not Comment | Prove filtering termination from progress/bounds and retain annotation/function side effects of discarded comments. Successful non-relevant return establishes safe entry; EOF is not automatically a new safe-entry gate. |
| expect_colon | next followed by token match | A successful result derives cached Colon and pending-none, then the enable-entry theorem. Failed match may have populated a Function and cannot establish safety. |
| expect_exhausted | Save, next, restore; returns failure on token | Token/observer/cache effects of the speculative read persist after cursor restoration. This is not an observer-neutral predicate. |
| try_parse | Save, execute callback, reset only on Err | Preserve callback effects; reset does not roll back cache, seen state or annotations. Callback contract must exclude unaccounted enable/query changes. |
| parse_entirely | Callback first, then expect_exhausted on success | Derive entry transparency and effects of exhaustion. A failed callback does not run that exhaustion path. |
| parse_until_before/after | Set combined stop; callback/exhaustion; restore old stop; conditionally raw-recover to delimiter; optional delimiter advance | Prove normal-return delimiter restoration, Stop-vs-Consume error behavior and observer-active recovery. Raw recovery does not replace cache. Brace delimiter cleanup and outer stop boundary matter. |
| parse_nested_block | Take pending block; depth rejection raw-cleans; otherwise set closing delimiter, run callback/exhaustion, raw-clean, restore stop/depth | Preserve tracking/annotations through both depth branches; treat panic/overflow and normal-return premises explicitly. Existing depth repair stays unchanged. |

None of these Rust helpers independently enables/disables the tracker. For a callback that does not reconfigure the observer, the existing epoch invariant is stable under their fresh/raw/cache/reset effects. Arbitrary externally supplied callbacks can reconfigure it; no generic safe-callback theorem may omit that precondition. The fresh whole-tree source inventory supports the identified production protocol but is not a formal completeness proof of every generated call edge or future caller.

## Counterexamples, publication and browser leads

Retained PublicByteWitnesses still exhibits `save → fetch var( → reset → enable → cached fetch` missing a Function, and query/re-enable replay doing the same. Calling next() instead of the primary API does not universally fix this: at the reset-to-Function position with no pending block or whitespace, its skip phase does nothing and the same cache hit can occur. The production routes above add the missing cold/Colon entry gate.

The annotation example retains both A-before-block-end raw replay and cached B no-write. next() often restores B by consuming the trailing comment raw, whereas comment-preserving callers may not. That is protocol-specific, not a proof of stylesheet publication. This audit supplies no actual stylesheet input reaching a wrong published map URL, and no new browser probe is warranted solely from the abstract witness. No generic last-sourceURL or CSS annotation normative contract is invented here.

The highest-value next work is formal wrapper admission, not another finite token matrix. Ranked requirements are in NEXT-TARGET.md. No source/native/WPT/Git/Firefox build or browser mutation was performed. No generated compiler targets were created, so there is nothing to delete from this task.
