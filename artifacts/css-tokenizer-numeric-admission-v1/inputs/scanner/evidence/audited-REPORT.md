# Resolved dependency scanner: source review

## Recommendation

Use the public cssparser API as a one-token suffix cursor. `scanner-proposal.rs` is a concrete, uncompiled helper proposal. At each iteration create `Parser::new(remaining)`, call `next_including_whitespace_and_comments` exactly once, inspect that token, advance by `position().byte_index()`, and discard the parser. No parser state crosses token boundaries.

Use it only in the two persistence sinks named by the authenticated design: the attribute branch of `substitute_references_if_needed_and_apply`, and the universal-registration branch of `Substitution::into_value`. `VariableValue::new_resolved` should first construct the ordinary `VariableValue::new` result, then install the returned flags if `Some`. Preserve bytes, URL data, first/last token types, empty reference list, and existing caller taint assignments. Leave every other constructor unchanged.

On `None`, retain the ordinary constructor's empty references exactly. This is a compatibility fallback for an explicitly unsupported domain, not a complete dependency summary. Never install partial flags accumulated before an unresolved function. Never interpret that function's unselected fallback as a selected dependency. Returning invalid-at-computed-value here would introduce a separate semantic change.

**Verdict:** suitable implementation design for valid, fully substituted values in these two sinks; no native patch, compilation, benchmark, browser execution, or formal verification was performed for this proposal. The unresolved environment payload domain remains unrepaired.

## Why the iteration is safe at arbitrary valid nesting depth

The local cssparser layout differs from older releases: there is no public standalone Tokenizer or ParserInput. Tokenization methods are on `Parser`. `next_unchecked` and the block marker in `ParserState` are crate-private. Avoid adding API or reaching private state.

`Parser::new` initializes fixed fields and a dummy cached token; it does not scan the input or allocate a nesting tree. Its first `next_including_whitespace_and_comments` sees no pending block and no delimiters. The cache is initially a miss. The tokenizer returns a complete lexical token, including any escapes, comment, string, or unquoted URL, and sets a pending block marker only after an opening token. Discarding the parser prevents the next-call block skip. Closing brackets are returned as ordinary closing tokens, not as `Err`, in this undelimited parser.

The next-token dispatcher and its numeric/name/string/URL/comment helpers depend on the remaining bytes. Previous line/column fields only affect source locations and bookkeeping. Arbitrary-function observation and source-map/source-URL comments update diagnostic tracking, not token classification. Fresh relative line positions therefore do not change these dependency flags. There is no document-start BOM special case in `Parser::new` to be reapplied at suffix boundaries.

The loop invariant is that `remaining` starts immediately after a complete token in the original byte string. Every nonempty successful iteration consumes at least one byte, ends at a UTF-8 boundary, and strictly shortens the suffix. It never starts inside a string, escape, comment, or URL token. It neither concatenates independently tokenized pieces nor reparses previously consumed input. Fixed-cost parser initialization adds O(number of tokens). The tokenizer itself has bounded lookahead; quoted `url(` detection can look across whitespace that the following whitespace token visits again, still constant multiplicity. Total source traversal remains linear, subject to the existing tokenizer's allocation/number parsing behavior.

There is no nesting stack, no recursive visitor, and no depth cutoff. Token decoding can allocate a string proportional to one escaped token, as the existing tokenizer does. This is not an allocation-failure or Rust memory-safety proof.

The helper is a summary under the caller's valid-value admission, **not a replacement CSS syntax validator**. Balanced closing tokens are intentionally inert; it does not diagnose unmatched closers or unclosed grouping. Adding structural validation would require a heap stack and CSS EOF-recovery rules, with no benefit to this summary's valid-input contract. `BadUrl` and `BadString` are explicitly rejected, but their rejection does not make the helper a general validity predicate.

## Why the obvious alternatives fail the requirement

| Alternative | Source finding / consequence |
| --- | --- |
| Repeated `next()` on one Parser | After an opener, the next call skips the entire block. Nested units disappear. |
| Recursive `parse_nested_block` walk | Default limit is 75. At greater depth it returns `TooManyNestedBlocks`. Successful original parsing does not bound the depth of values assembled by later substitution. |
| Disable the limit | Removes the parser's recursion guard and permits unbounded call stack use. |
| Return zero flags beyond a chosen limit | Silently loses dependencies in valid substituted input. |
| Queue block slices using the high-level parser | Finding each enclosing block's end can revisit descendant bytes at every depth. Avoid a quadratic implementation. |
| Existing block skipper | `consume_until_end_of_block` is iterative with `SmallVec<[BlockType;16]>`, but private and discards tokens. It does not expose the desired visitor. |
| Scan original references / OR all inputs | Includes unused fallback flags and can miss token boundaries created or separated by serialization. |

The existing `nested_block_limit` and `no_stack_overflow_multiple_nested_blocks` tests exercise parser limits/skipping, not the proposed traversal. Neither was executed here.

## Token semantics

Only `Token::Dimension { unit, .. }` contributes `ReferenceFlags::from_unit(unit)`. It already handles ASCII case and the current em/ex/cap/ch/ic, lh, rem/rex/rcap/rch/ric, and rlh groups. Tokenization decodes escaped identifiers before the unit classifier sees them. Numeric exponent recognition remains the tokenizer's job.

Strings, comments, unquoted URLs, identifiers, at-keywords, hashes, percentages, numbers and delimiters contribute nothing. Ordinary functions and grouping are traversed by the flat stream. A quoted URL is a `Function("url")` plus a `QuotedString`, so its string contents remain inert. Do not blindly skip the entire `url()` function: this proposal follows lexical token semantics, including actual tokens outside the string, rather than inventing a URL-modifier grammar. Bad URL recovery produces one `BadUrl` and returns `None`, preventing recovered text from masquerading as a valid summary.

Use the same `SubstitutionFunctionKind::from_ident` classifier as the existing declaration parser for unresolved `var`, `env`, and `attr`. Escaped function names are decoded by `consume_name`; this is not a byte-substring search. The domain is Firefox's three recognized arbitrary substitution functions, not a claim to implement every new CSS function.

Re-tokenize the final persisted bytes, including separators. `1/**/em` has no dimension; `1em` does. `VariableValue::push` separator behavior therefore remains authoritative. No textual search for `em` can replace tokenization.

## Environment payload boundary

`CssEnvironment::get` treats names beginning with `--` as link parameters, parses their arbitrary CSS through `VariableValue::parse`, and returns it. The code already records bug 2028998. The `Env` arm of `substitute_one_reference` immediately calls `Substitution::from_value`, which carries CSS/token types/taint but no recursive resolution of that returned reference list.

Thus successful outer substitution can yield `var(--x, 1em)` or `1rem var(--x, 1em)`. Neither is admitted as fully resolved. Return `None` for the entire output, including the latter's earlier `1rem`; preserve the former empty metadata rather than asserting completeness. An outer ordinary function containing such an unresolved function must likewise return `None`. Inert string or URL text spelling `var(...)` must not trigger this branch.

Built-in environment evaluators use generated pixel, number, millisecond, identifier, or fixed color-scheme values in the inspected source. Link-parameter payloads with a resolved `1em` are handled normally. This audit does not establish all document/URL/provider admission for link parameters or fix their recursive substitution semantics.

## Typed generated values and the two sinks

`Value::to_variable_value` serializes typed values with the general constructor, while its universal arm clones the original value. Do not change that shared constructor: computed typed values have different staging and commonly canonical units.

Typed attribute results and numeric unit-form attribute results pass through `Substitution` and reach the attribute persistence sink. Scanning their emitted bytes captures specified relative dimensions where they actually survive serialization. Raw-string attributes serialize quoted strings and remain inert. Typed custom properties that are already computed do not need their canonical serialization to resurrect specified dependency flags. The universal persistence sink must preserve remaining specified dimensions for a later typed consumer. These statements are a source-path review, not proof of every serializer or graph evaluation order.

`COLOR_SCHEME` remains registration policy. Root-relative remapping remains `for_each_non_custom` policy. The scanner does neither. Original declaration parsing still has its broader identifier/fallback flag collection, untouched by this fix.

## Spec / source / test map

CSS Syntax's token-consumption algorithms distinguish numeric dimensions from strings, URL tokens, comments and identifiers, with escapes decoded during name consumption. This supports delegating lexical classification to cssparser rather than a new lexer. [CSS Syntax](https://drafts.csswg.org/css-syntax-3/#tokenization).

Registered-property dependency rules supply the downstream font and line-height edges. Attribute substitution determines the selected value before these persistence points. This scanner reconstructs surviving unit metadata; it does not replace graph-cycle or substitution algorithms. [Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles), [CSS Values](https://drafts.csswg.org/css-values-5/#attr-substitution).

Complete local source snapshots are under `source/`; the design's exact source/spec closure is under `design/`. `DESIGN-AUTHENTICATION.json` records authentication of all 15 design inputs before reuse. Searchfox discovery transcripts are under `discovery/`; indexed line positions can differ from local snapshots. Current web retrieval is retained in `spec/WEB-RETRIEVAL.json`; direct urllib retrieval failed DNS and is not represented as a successful raw-page capture. The design supplies authenticated full Values/Properties HTML and retrieval metadata.

`CASES.json` contains suggested unit-level inputs with independent lexical expected summaries. They are **UNEXECUTED**. The depth cases must call the helper directly, avoiding a shallow source parser gate; a browser case can also assemble deep output from individually admitted custom-property values. Existing root browser graph failures remain external evidence for the metadata loss, not evidence that this proposed scanner works. No new WPT execution or metadata claim is made here.

## Implementation gates and proof obligations

1. Compile the actual helper in Stylo; verify exactly two new-resolved call sites and no general-constructor changes.
2. Unit-test every proposed token family and unresolved sentinel, including depth far above 75, both unit groups at different depths, adjacent comments, escaped names and quoted URLs. Confirm no timeout/stack failure; no arbitrary maximum depth in the helper.
3. Repeat the existing exact graph/browser corpus and include selected-primary versus unused-fallback controls. Keep unresolved link-parameter behavior explicitly separate until provider semantics are repaired.
4. Prove the summary fold over complete lexical tokens and the strict suffix-progress invariant. Bind the token refinement to the actual cssparser implementation; a list-token theorem alone does not establish native correctness.
5. Prove the two sinks preserve all non-summary fields and reference-list emptiness under resolved admission. General environment resolution, serializer equivalence, graph/Tarjan correctness, arbitrary CSS support and allocator behavior remain outside this scanner component.

No static blocker was found for the proposed suffix cursor. The compatibility fallback is intentionally incomplete for unresolved outputs and must remain visible in the final repair/report.
