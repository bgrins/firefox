# Parser cache observer admission

## Result

Two original public-API counterexamples remain valid. No browser-reachable regression is established by this investigation. A new universal tracking-epoch theorem supplies a sufficient condition, with source-derived entry conditions for the discovered Firefox production callers. URL publication remains open across arbitrary stylesheet retry histories. This component does not weaken the original public-stream obligation or address depth-limit recovery.

The prior scout was authenticated against all 175 manifest entries before its code was reused. Its original report, witness and observations are retained unchanged under `prior/`. Current discovered source snapshots and prior comparisons are recorded in `SOURCE-PINS.json`; the parser snapshot includes the parent's separate depth-recovery change, retained as a source delta. No native, WPT, Git, build-system or browser actions occurred here. The only compilation is standalone Rust dependency/source execution and Lean kernel checking.

## 1. Tracking: useful sufficient condition

`look_for_arbitrary_substitution_functions` resets the observer to LookingForThem. `seen_arbitrary_substitution_functions` reads it and disables tracking. Neither operation invalidates the cached token. A fresh Function invokes `see_function`; returning that Function from the cache does not. Parser reset restores only ParserState, not either observer or the cache.

`TrackingEpoch.lean` proves equality with an independent list of logical observations over arbitrary finite histories of fresh public tokenization, raw tokenization during block skipping, cache hits, and resets. The invariant is derived: a relevant cached Function implies that the native seen bit is already true. Fresh tokenization updates the cache and observation; raw tokenization updates observation without replacing the cache; reset/cache replay retain the native bit. The reference emits the cached relevance on every logical cache hit and takes Boolean existence over the resulting list. The native side never does that on a hit. Their equality is therefore conditional and non-definitional.

The initial condition is a cold cache or a cached token that cannot be a relevant Function. `colon_entry` derives it for every previous state by consuming a non-Function token and beginning the epoch. `prefix_inv` proves it for every subsequent prefix. Late enable and query/re-enable with a relevant old cache are explicit proved counterexamples, not excluded by changing the public contract.

### Actual caller entry audit

Searchfox's whole-tree lookup finds two production enable sites and two production sites that query the observer (four query expressions). Source snapshots cover the complete bodies and their direct entry callers.

| Entry | Cache condition at enable | Evidence and boundary |
|---|---|---|
| geckolib `compute_arbritrary_substitution_functions` | Cold cache | Creates Parser::new immediately before enabling; no token read in between. |
| `parse_one_declaration_into` → PropertyDeclaration::parse_into | Cold cache | Fresh parser; parse_entirely invokes its closure before its exhaustion check. |
| RuleBodyParser → DeclarationParserState::parse_value → PropertyDeclaration::parse_into | Colon cache | Iterator expects a colon immediately before parse_value. Delimiter wrappers invoke their closures before recovery/exhaustion. Property lookup/context operations do not read this parser. |
| supports Declaration::eval → PropertyDeclaration::parse_into | Colon cache | Creates a fresh parser, reads ident and colon, then enters value parsing. Evaluation does not reuse the speculative supports-condition parser. |

PropertyDeclaration::parse_into skips whitespace/comments, then saves the value start. That skip uses raw comment consumption and cannot install a Function cache. Its noncustom helper enables tracking before reading the first value token. Even a prior speculative history cannot preserve a Function cache across the successful colon read: either that read installs a Colon, or it returns an already cached Colon. The theorem's fresh-non-Function constructor describes the resulting projected state in both cases; it does not assert that a native Colon read always misses the cache.

The helper's two outcomes also matter. A failed property parse keeps tracking enabled while scanning the remainder. A successful parse queries/disables tracking; if it found a function, the result is retained in the local `saw_arbitrary_substitution_functions` Boolean and ORed with the later query. The short-circuit OR is intentional. Wide-keyword success queries/disables before returning. This audit does not replace those branches with one indefinitely enabled native observer.

**Admission limit:** the Lean theorem is an event-level component. Actual raw-byte parsing, ASCII-insensitive function recognition, generation of those events, native allocation/bounds, and a complete proof of all generated property parsers are not lowered into Lean. The source audit establishes these entry conditions; the theorem does not certify all Rust execution or any future caller. Relevant-function classification is fixed during an epoch; nested re-enabling/querying on the same parser needs a new epoch argument.

## 2. URL metadata: obstruction retained

The original sequence on `(/*# sourceURL=A */)/*# sourceURL=B */` saves state after the opener, skips the block and caches B, resets, reconsumes A through raw block skipping, then returns cached B without its observer effect. EOF state holds A. The sourceMappingURL variant behaves identically. These are legitimate public API histories, so unconditional final-metadata equivalence is false.

The new native witness retains both and adds two discriminating controls:

- Replaying via next() consumes the trailing B comment in skip_whitespace, restoring B.
- Reopening the block through parse_nested_block(expect_no_error_token) replaces the cache while consuming A; the outer B comment is freshly tokenized, restoring B.

Both controls reach the same raw EOF. They validate exact protocols, not all stylesheet histories.

The direct Servo comment-preserving consumers are custom-property parse_declaration_value_block and Servo_CSSParser_NextToken. The latter constructs a fresh Parser per token call and does not publish its URL observers. **That direct search is not a complete consumer inventory:** cssparser::expect_no_error_token uses the same API and is called by supports parsing, general-enclosed query parsing, style-range function parsing, and forgiving selector recovery. Those complete discovered sources are retained. Supports' failed nested parse retries through parse_nested_block(consume_any_value), corresponding to the second control, rather than the original skip-only witness. This excludes that exact witness shape for that retry; it is not a global supports/selector proof.

Stylesheet::parse_rules publishes current_source_map_url and current_source_url after StyleSheetParser exhaustion. StyleSheet exposes them, with response-header precedence for maps. To claim a browser defect still requires an actual stylesheet parser path that leaves B cached while raw replay of an earlier comment overwrites its observer, followed by no fresh consumption restoring the final annotation. No such concrete caller trace was established. Full property/selector/query retry admission therefore remains an actual open proof obligation, not an assumed safety condition.

## 3. Contract and specification

Fresh primary retrieval is retained in `spec/`. The September 11, 2026 ECMA-426 draft's JavaScript extraction scans trailing comments/whitespace in reverse and stops at code. CSS extraction is described as analogous using block comments. Therefore the original trailing-B example supports B as an extraction inference; a generic "last annotation anywhere" oracle is too broad. The document does not define cssparser reset or cache semantics. Its sourceURL discussion does not supply a precise corresponding CSS extraction algorithm. See `SPEC-TRACE.md` for separate verdicts.

The tracking expectation has a stronger library contract basis: the public documentation promises whether a relevant function has been seen since enabling. A cached public Function is returned after enabling in the counterexample. This is an API discrepancy under that interpretation, not an established CSS parsing violation.

## 4. Evidence and remaining scope

Fresh relocated replay checks 2 Lean modules / 10 theorem axiom audits, two compiled semantic mutants, and 14 exact native cases. The mutants remove fresh/raw tracking updates; each altered definition and counterexample compiles, while unchanged theorem proofs fail. No syntax failures are counted. Finite Rust results are correspondence evidence, not a universal native proof. `check.py` authenticates the complete manifest before replay; relocation and tamper receipts are retained.

All 12 original tokenizer obligations remain preserved in `PROOF-TARGET.md`. Prior comment/string components are unchanged. This package advances obligation 8's tracking-history admission and clarifies obligation 9's publication obstruction. Raw UTF-8, byte/cursor correspondence, line state, compiler/library primitives, bounds, broader public histories, evaluator/CSSOM and source-URL observer reachability are not closed by this event model. No new native repair is proposed here.
