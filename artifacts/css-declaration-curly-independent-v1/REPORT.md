# Independent declaration curly fallback review

Date: 2026-10-19. Recommendation: accept the narrow native reset and its WPT.
No blocking source, normative-oracle, or paired-browser issue was found.
This recommendation is separate from the proposed universal declaration
component proof, which is still in progress.

## Exact reviewed inputs

The static capsule `css-declaration-reparse-static-v1` has 162 authenticated
inputs. Its manifest is `be11ba093332bb80969efac104d8c61113d02f25592395e82deda65c30cf8299`
and freeze is `bb69319b1e6c4917c3c747439ac0ee30602f3d9f434dcc8309d57cc171b9eedd`.
The final browser capsule `css-declaration-curly-final-browser-v1` has 34
authenticated inputs, manifest `fb7ad93158892a1163537020d224d3a830a1fd66f8c668c6a3570fe32c6cb2b4`
and freeze `7d506ad6b395eeccc090646d760d14feee43878592a3b5a0f05345ab171707d1`.

The complete original properties source is
`4ba82684d7ca10e3f180aa3694b139f89eab7238cb46e6573cd39dce63781d47`;
candidate is `6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92`.
Their exact difference is the inserted `input.reset(start)` and the existing
comment's replacement. The WPT is
`91f53a6374da006d1243256356e43a0554387db8ee0b6bdcc29729c3cb3c4ab7`.
The two-file patch is `94e0730424570c206d35f9f35017407e8171c886f0453f1aa77b8377aafbb4ec`.

## Rule, cause, and production connection

The rule is reached: ordinary declarations cannot mix a top-level curly block
with another significant component. A lone curly block, blocks inside other
components, and custom properties have different treatment. Arbitrary
substitution defers property grammar checking but does not waive this structural
restriction. See the independent current-primary [spec trace](SPEC-TRACE.md).

The complete noncustom helper, its `PropertyDeclaration::parse_into` caller,
declaration-list entry and cleanup, font-family providers, and cssparser
reset/next/comma-item functions were read. Fresh parse-one-declaration entry and
declaration-list/nested-rule entry both reach the same helper after saving the
start of the value. Custom-property entry branches away beforehand. The actual
`FontFamily::parse` uses comma-separated `SingleFontFamily::parse`; the generic
`serif` item succeeds locally, but its unexpected trailing block causes item
failure. The real comma-item parser's consume-on-error cleanup traverses that
block and sees its substitution function before returning the error.

The old helper validates only the remaining suffix. That suffix can be empty,
while the sticky substitution observation remains true. It consequently reaches
`VariableValue::parse`, which is deliberately permissive about curly blocks,
and publishes an ordinary property with deferred variables. The bug is lost
structural validation after property-parser recovery, not a failure to recognize
the substitution function.

Resetting to the saved start makes the existing top-level component loop inspect
the entire value. `next()` skips whitespace/comments and consumes pending nested
blocks as components. A curly first component is permitted only as the whole
value; a later curly component or any component following a first curly block
is rejected. The first-lookahead flag remains valid for that same saved start.
Stop delimiters, parser identity, namespaces, and URL context are unchanged.
The second reset before the actual variable-value parser remains intact.

### Observer and publication details

- Ordinary successful parses without substitutions return before the new reset.
- Successful parses with substitutions store true locally before querying
  disables tracking. The later Boolean OR preserves that fact; validation itself
  does not need the tracking epoch to remain enabled.
- Failed parses retain enabled sticky observation. Parser reset restores cursor
  and pending-block state, not that observation. Re-enabling the tracker would
  be a different change and could discard an observation of a cached function.
- CSS-wide keyword early return is unchanged. Scratch publication/exhaustion and
  `did_error` cleanup remain the callers' existing responsibilities. A failed
  structural scan cannot reach the later `parsed_custom` callback.

This source reasoning does not prove arbitrary successful generated property
parsers obey the CSS declaration grammar. The unchanged early-success path
continues to rely on that provider contract. Comment URL/source-map observer
histories and all allocation/compiler semantics are also not proved here.

## Independent replay and its limits

After authenticating all inputs, a manifest-only copy was replayed from
`/private/tmp/curly-independent-v1/capsule`; output was a separate directory.
The replay rebuilt the retained complete cssparser and dependency sources and
the exact extracted helper. Exit was zero: 26 observations per variant, seven
forbidden original gateways, zero candidate forbidden gateways, and exactly
seven changed rows. Retained commands and raw result are under `evidence/`.

The witness uses real cssparser comma-item recovery but a reduced identifier
callback, not the complete Stylo font-family parser. Its `VariableValue::parse`
adapter accepts at the gateway. It therefore establishes helper control flow,
not complete arbitrary-value acceptance. The producer's component oracle uses
a fresh parser and independent top-level counting, but shares tokenization and
block skipping. Our checker independently classifies the fixed simple fixture
values; this is bounded evidence, not a second tokenizer implementation or a
universal theorem. No Lean proof or mutation gate is claimed by this static
capsule. The browser pair supplies the actual production acceptance observation.

## WPT oracle and final pair

The 12 values through four APIs produce 48 new subtests. Prior `monospace`/`blue`
declarations distinguish parse-time rejection from invalid-at-computed-value-time
fallback. CSS.supports checks parse-time support directly. Following opacity
checks distinguish declaration rejection from accidental loss of the rest of a
declaration list. No font, layout, animation, or timing dependency is present.

All six malformed substitution values fail through all four APIs on the
baseline and pass with the candidate. Whole-curly, square-block, plain var,
custom-property, no-substitution and color controls discriminate the rule and
the consuming font-family path. Existing `var-with-blocks.html` tests the rule
with color, whose failure does not hide the offending component; it remains a
useful unchanged regression test.

Our checker reads raw JSONL using unique `(action, test, subtest)` keys and
rederives the exact 24 expected improvements, rather than trusting PAIR-CHECK's
counts. The final pair has 94 keys: 89 candidate subtests PASS and five harness
OK; 70 outcomes unchanged, including 41 existing subtests. Input/before/after
pins are equal within each phase. The sole changed fixed input is the properties
source, with the exact WPT unchanged. Candidate build input/source identities
connect to browser input; the forced Rust rebuild and final link both exit zero
and their log hashes match. The link log retains four build-monitor
`KeyError: export` traces despite successful exit and XUL link; it is not a
warning-free log. This is a shared-worktree macOS pair, not an isolated
upstream runtime run.

The retained WPT lint succeeds. Rustfmt's changed hunk is stable. Whole-file
formatting detects an unrelated pre-existing wrapping difference in both
variants; it was not folded into the patch. The first wrong-edition formatting
attempt is retained as history, not represented as a successful check.

## Compatibility, performance, and packaging

The extra work is a consumed-prefix rescan on fallback/error paths, bounded by
one additional whole-value scan per helper invocation under normal parser
progress. Ordinary successful parsing and CSS-wide early returns avoid it.
This is source-level cost reasoning; no zero-overhead claim or performance
benchmark was made. Nested-block traversal retains existing resource limits.

The two-file patch contains only `servo/components/style/properties/mod.rs`
and `testing/web-platform/tests/css/css-syntax/declaration-curly-fallback.html`.
Independent artifact-only patch application/reversal reproduces the exact
retained original/candidate and WPT. Root's separately retained PATCH-CHECK
reports successful application/reversal on stack base `b2308963638e11e8c1403683c2a0da451b339353`
and upstream `976279105b2e78b8666a959eb3f25c9176cefaf8`; no Git command or
isolated-upstream build was run by this reviewer.

Public known-issue searches were bounded. Bug 2077906 concerns DevTools hiding
valid custom-property declarations despite correct CSSOM, a different layer
and different rule. CSSWG issue 9317 supplies the normative history. No exact
duplicate was identified; novelty is not established.

## Remaining gates and scope

There is no remaining blocking gate for this narrow native/WPT recommendation.
Root still owns final acceptance and commit organization. The separate universal
component/rewind proof, full native tokenizer-to-component admission, exhaustive
generated property grammar, substitution/cascade evaluation, compiler/heap
semantics, and isolated upstream runtime are not completed by this review.
The static producer's FORMAL-PLAN preserves those distinctions.

`COMMIT-ROSTER.json` lists exact source-companion and minimal native inventories.
No temporary binaries or rebuilt rlibs belong in that inventory. Recheck with
`python3 -I -S check.py`; add `--replay /private/tmp/new-empty-path` for a fresh
relocated native replay. Python 3 and the rustc path recorded in the producer
replay are external tools. Both authenticated sibling capsules must accompany
this review; `--artifacts` selects their containing directory after relocation.
