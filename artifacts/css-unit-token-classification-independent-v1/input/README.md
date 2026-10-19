# Dimension-only dependency classification proposal

## Status and replay

Artifact-only candidate, not compiled or browser-tested by this author. The retained source/spec audit predicts seven failing rows and seven passing controls on the original parser. That prediction is not an observed runtime result. Parent owns execution and acceptance.

Run `python3 check.py` from any directory. It authenticates inputs, verifies the exact one-hunk source transformation, applies and reverses the combined patch in a temporary tree, compares all resulting bytes, and runs Node's JavaScript syntax checker. Python 3, `patch` and Node are required. No checkout, native build, browser, Rust test harness or network is required for this replay. The checker is an integrity/packaging check, not a parser proof.

## Native change

`BASE.json` binds the complete original and candidate `custom_properties.rs`. Original SHA-256 is `71a507cba6ed20b40e690c29555844514870530a5bccc74e41459aa12e46d5bc`, the parent's final formatted resolved-summary candidate. The prior unformatted base and its formatting-only delta are retained. This package preserves the resolved scanner, both persistence sinks, namespace/tombstone/preload/typed-eligibility repairs and all other original bytes.

The single change in `parse_declaration_value_block` guards `ReferenceFlags::from_unit(value)` with `matches!(token, Token::Dimension { .. })`.

| Token | Candidate behavior |
| --- | --- |
| Dimension | Classify its decoded unit exactly as before |
| Ident, AtKeyword, Hash, IDHash, UnquotedUrl | Do not classify token text as a dimension unit |
| Other token variants | Unchanged |

The common arm and its escaping, U+FFFD repair, URL closing, token serialization metadata and cursor handling remain unchanged. The guard follows the existing token-discriminant inspection in that same arm; no new parser invocation, allocation or side effect is introduced. This is a source review, not a performance measurement or compiled type-check claim.

The original parser scans syntactic values, including fallbacks. This proposal does not change selection timing or settle relative dimensions in unused fallbacks. The newer resolved-output scanner is a separate repair; this patch changes only original declaration parsing.

## Proposed landing inventory

`fix.patch` concatenates `native.patch` and `wpt.patch`. It touches exactly:

- `servo/components/style/custom_properties.rs`
- The new WPT path in `WPT-PATH.txt`.

The optional `actual-parser-tests.rs`, snapshots, reports and checker are companion evidence, not additional production edits. Exact application is verified against the retained full base; applicability to another revision requires checking that revision. No Git operation was used.

## WPT and normative source

`registered-property-unit-token-dependencies.html` contains 14 direct computed-value tests. Its case data is exactly the original diagnostic case set with static prediction fields removed. The final WPT omits separate support/calibration diagnostics and retains meaningful controls: ordinary/identifier-only values, genuine relative-unit cycle, absolute length, quoted URL, ordinary invalid hash and absent font back edge.

For identifier and URL rows, direct custom-property readback exposes incorrect invalidation that font-size alone would hide. For invalid `@em` and `#em`, the registered property should reset to 11px and supply that value to font-size; false cycle detection instead invalidates font-size itself. URL cases contain no attr() source/taint and require no resource load. CSSOM canonical URL text is computed against the document base.

`evidence/REPORT.md` retains the primary-spec derivation and the distinction between a number-plus-unit Dimension token and identically spelled inert text. Its historical statement that no patch was supplied applies to the earlier audit. Complete historical source snapshots and primary spec bytes are retained with their pins. `evidence/INPUTS.json` is the historical audit manifest, not a claim that every historical diagnostic is duplicated here; the current manifest covers every file in this package.

## Actual-parser test feasibility

`actual-parser-tests.rs` is an optional child-module fixture for `custom_properties.rs`. It calls the real private `parse_declaration_value`, inspecting `ReferenceFlags` and missing closing text. It avoids a surrogate classifier and avoids initializing Gecko URL/context providers. It covers 18 token/flag cases plus three shared escaping/URL repair cases. It has not been integrated or compiled and is excluded from `fix.patch`.

Searchfox discovery of `servo/tests/unit/style/custom_properties.rs` and its module registration is retained. That indexed file contains old bench APIs inconsistent with the current local source, so it is not asserted to be a working current integration target. Root must select and compile a suitable actual style-crate test harness before treating the fixture as an executed source test.

## Explicit limits

No universal tokenizer, syntax-admission, SCC or full cascade proof is supplied. Registered-property graph behavior and CSSOM expectations require runtime validation. This package does not repair arbitrary Hash syntax, taint handling, unused-fallback timing, unresolved substitutions or provider behavior. The precise source delta is independently reviewable; runtime acceptance remains pending.
