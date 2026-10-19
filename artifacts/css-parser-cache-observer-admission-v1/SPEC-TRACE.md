# Observer contract trace

Fresh primary: https://tc39.es/ecma426/ (draft September 11, 2026), retained with retrieval time and hash.

1. Inline-annotation linking permits extraction methods, requiring agreement for unambiguous links.
2. JavaScriptExtractSourceMapURL examines trailing comments/whitespace in reverse and returns the first matching annotation; code stops that search.
3. CSSExtractSourceMapURL describes analogous extraction using block comments. MatchSourceMapURL accepts the original trailing `# sourceMappingURL=B ` content.
4. Inference for the original trailing-B input: B is selected before earlier code is relevant. This does not define arbitrary parser-reset observer state.
5. Actual publication requires Stylesheet::parse_rules to reach the counterexample's cache history; this source-derived reachability step is unresolved.

Verdicts: extraction inference **REACHED B**; browser violation through an actual stylesheet history **INCONCLUSIVE**. General last-annotation-anywhere claim **NOT ESTABLISHED**. CSS sourceURL normative ordering **INCONCLUSIVE**; retained library behavior and tests are implementation evidence.

Tracking is a library API contract, not a CSS Syntax requirement: tokenizer.rs documents observation since enabling, while parser.rs cache replay restores only ParserState. The manual late-enable history violates a logical-public-read interpretation. Actual production entry histories audited here meet the stronger epoch initialization condition; no browser failure follows from the generic API witness alone.
