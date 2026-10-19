# Retrieval record

2026-10-19. Primary CSS Values 5 opened via web tool at #attr-substitution. Same-day full HTML snapshot copied only after authenticating prior manifest 3491f31067701d4779f949dbdb232d6542e57056614ed56b86433c2879dfdeb9. Direct HTTP attempts failed DNS; spec-fetch.json and bug-search-fetch.json retain failures.

Searchfox CLI discovery commands/output in searchfox-0.json and searchfox-1.json. Later `searchfox-cli --define parse_declaration_value_block -l 300` failed DNS (empty redirected searchfox-parser.txt is not evidence of successful retrieval).

Web Searchfox URL https://searchfox.org/firefox-main/source/servo/components/style/custom_properties.rs showed indexed revision e2c1c288 dated 2026-10-09. Its fallback parser creates a separate References collection and stores it on VariableFallback; only summary admitted, no full-source identity claim.

Queries: `site:bugzilla.mozilla.org attr fallback chained attribute CSS`; `site:github.com/servo/stylo attr fallback references`; `"attr" "fallback" site:bugzilla.mozilla.org/show_bug.cgi`; `"attr" "preload" site:bugzilla.mozilla.org`; `"attr" "fallback" "type" site:github.com/w3c/csswg-drafts/issues/11500`. Relevant primary Bugzilla hits2006626,2034337,2067875 were triaged as described in REPORT. Direct CSSWG issue11500 web retrieval failed; current spec and retained Bugzilla2051901 discussion supply the used/unused fallback constraint.

Bugzilla captures were retrieved via tools.mcp__moz__get_bugzilla_bug; their text is retained as BUG-*.md. Bug2021155 was read but its full returned text was not persisted; no verbatim quote or exhaustive issue audit relies on that uncaptured item.
