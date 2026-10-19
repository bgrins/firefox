# Independent cache-observer admission review

## Recommendation

Accept the conditional tracking-epoch component and the source-entry audit. No blocking model/source mismatch was found. It establishes a useful sufficient condition for the discovered production entry paths, not an unconditional public-parser or browser URL theorem. Both original public-API counterexamples remain retained, and all twelve tokenizer obligations remain in scope.

All 208 producer inputs were authenticated before producer execution. The fresh replay used a manifest-only relocation in /private/tmp/cache-observer-independent-v1/capsule. It completed successfully: one proof module plus its Audit module, exactly ten unique theorem audits, two compiled Lean semantic mutants, fourteen native observations, and four authentication-before-execution tamper rejections. The restored capsule authenticated successfully afterward. Exact logs are retained under evidence/.

## Model reading and independent reference

The complete TrackingEpoch model and Audit module were read. State.cache records whether the cached token is a relevant Function, not whether a cache entry exists. Cold and cached-nonrelevant states intentionally project to false. State.seen represents the enabled observer's sticky observation bit. The function-relevance classification is fixed for the epoch.

nativeStep updates seen for fresh public tokenization and raw tokenization; only fresh tokenization replaces the cache. Cache hits and reset do not update either projected field. The reference separately emits a list of logical observations: fresh/raw events emit their relevance, cache hits emit the cached relevance, resets emit nothing. Taking Boolean existence over that list is not definitionally the native sticky bit: the cache-hit branch deliberately differs.

Inv is exactly the missing implication needed to bridge those branches: if the cache holds a relevant Function, it must already have been observed. step_inv and prefix_inv derive its preservation, while step_seen and execution connect arbitrary finite histories to the independent observation list. The initialization premise is explicit. cold_epoch derives the result from false/false. colon_entry normalizes any previous state by a fresh-nonrelevant projection before beginning tracking; its proof reduces to cold_epoch. This does not independently prove that every actual native colon is a cache miss. A cached Colon has the same cache=false postcondition, as the source audit explains.

The late-enable and query/re-enable theorems demonstrate genuine excluded initial states. They are not removed by an invariant assertion or relabeled as unreachable public API calls. The theorem has no query/disable/re-enable event inside an epoch. Native histories crossing those operations need another epoch argument and explicit accumulation of prior results. The production helper's success branch and short-circuit Boolean OR are therefore essential source obligations rather than details the model can erase.

The reference is independent at the event-semantics layer. Native byte parsing, cache key identity, callback schedules, ASCII-insensitive function decoding, and event generation are not derived by these ten theorems. This limitation is accurately retained in the producer report.

## Source entry and caller audit

The complete observer setter/query/see_function bodies, Parser construction/reset/cache read, skip-whitespace path and delimiter wrappers were inspected, together with the relevant production call chains. The 23 retained source pins authenticate exact snapshots; the three cssparser files compiled by native replay equal their source snapshots.

- Parser::new installs a Semicolon sentinel with an impossible cache start position and DontCare tracking. The geckolib substitution helper creates this parser and enables tracking before its first read.
- parse_one_declaration_into creates a fresh parser. parse_entirely invokes the supplied closure before its exhaustion check, so no hidden value-token read precedes PropertyDeclaration::parse_into.
- RuleBodyParser successfully expects Colon immediately before calling the declaration value callback. DeclarationParserState does property/context work and enters the bang-delimited wrapper before PropertyDeclaration::parse_into. The wrappers call their closures before recovery. A successful colon read either installs Colon or returns a cached Colon; either has relevance=false.
- supports Declaration::eval creates a separate fresh parser, consumes the declaration name and colon, and enters value parsing. It does not reuse the condition parser that originally recorded the declaration text.
- PropertyDeclaration::parse_into skips whitespace/comments before saving the value state. At these entries no pending block exists. That skip performs raw comment consumption without installing a Function cache. Its general skip_block_at_start branch is not an unconditional statement that every arbitrary skip call is harmless; the entry premise matters.
- parse_non_custom_property_declaration_value_into enables tracking before its first value token. Failed parsing retains tracking during the remaining scan. Successful parsing queries/disables tracking, retains a true observation in the local Boolean, and later ORs it with the final query. Wide-keyword success queries/disables before returning. The model does not treat these distinct phases as one indefinitely enabled observer.

The source inventory identifies two production enable sites and the corresponding query expressions. It is a retained discovery/source audit, not a machine-checked whole-program or future-caller completeness theorem. The generated property parsers and nested callbacks still require event/source admission for a universal native result.

## Native replay and mutation interpretation

The standalone build compiles the full retained cssparser and dependency sources, with optional fast-match/color/serde/malloc feature boundaries as recorded. It does not replace the parser with the Lean model. The fourteen observations are six cold/colon/nested-function entry-prefix cases with and without reset, two late-enable cases, and six URL-history cases covering both URL fields and three replay protocols. The native assertions establish their expected outcomes; the independent checker separately checks exact named rows and values.

The two semantic mutants are Lean definition changes, not native Rust mutations. Each modified definition plus a distinguishing witness compiles. The unchanged theorem source then fails with semantic unsolved goals/type mismatch. No syntax or unknown-name failure is counted. The native suite is bounded source correspondence, not a universal native proof.

The producer replay checks the audit count and allowed axioms. This independent checker additionally enforces the exact ten theorem names against both source declarations and fresh audit output, so duplicate or omitted audits cannot pass this review merely by preserving a count. The four tamper gates change model, witness, native source and manifest; all reject before the requested replay destination exists.

## URL histories and specification limits

The counterexample preserves both sourceURL and sourceMappingURL histories: raw replay of A overwrites the observer, then a cached B comment returns without restoring B's side effect. Both variants reach raw EOF with A. Replaying through next(), or reopening the block through parse_nested_block(expect_no_error_token), freshly consumes B and yields B. These are protocol-specific observations, not proofs about every stylesheet retry.

The producer correctly keeps broader indirect comment-preserving consumers in view: expect_no_error_token and its supports/query/selector callers prevent a direct-API-call search from proving completeness. Stylesheet parsing eventually publishes the observer fields, but no exact production trace connecting those publishers to the bad cache history has been established here.

The retained ECMA-426 trace supports a trailing-B extraction inference for sourceMappingURL and explicitly avoids a generic last-annotation-anywhere rule. It does not specify cssparser reset/cache operations. CSS sourceURL ordering remains inconclusive. Consequently this review accepts the source/API obstruction and conditional tracking result without asserting a browser defect or proposing a native repair.

## Original obligations retained

| Original obligation | Current disposition |
| --- | --- |
| 1. Raw dispatch/entry | Production epoch entry conditions audited; full byte dispatch remains open. |
| 2. Preprocessing | Unchanged, not proved by the event model. |
| 3. Borrowed strings | Earlier component unchanged; no new ownership claim. |
| 4. Owned strings | Earlier component unchanged; codec/heap boundaries retained. |
| 5. Escapes | Earlier component unchanged; no new native codec admission. |
| 6. EOF/bad newline | Unchanged. |
| 7. Comments | Earlier component unchanged; observer cache histories remain distinct. |
| 8. Public stream | Conditional tracking epoch proved; full next/reset/cache/block execution remains open. |
| 9. Observers | Tracking initialization clarified; URL publication reachability and line/byte state remain open. |
| 10. Native bounds | Allocation, usize, packed metadata and compiler/library normal completion remain admitted. |
| 11. Evaluator/CSSOM | Open; no browser URL violation established. |
| 12. Replay/independence | This component's replay, exact audit and mutation/tamper gates pass; full-provider completion is not inferred. |

## Handoff

PRODUCER-COMMIT-FILES.txt lists the exact 208 producer inputs plus MANIFEST.json/FREEZE.json, 210 files. REVIEW-COMMIT-FILES.txt lists this review closure. Do not stage unlisted compiler products, development directories, caches, or the temporary relocation. The component includes no production patch.

The next substantive gate is source-derived public event generation and query/disable epoch composition, or a concrete stylesheet retry trace for the URL obstruction. More copies of the fourteen native fixtures would not discharge those obligations.
