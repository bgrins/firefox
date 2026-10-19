# Independent review: dimension-only unit classification

## Verdict

Approve the exact one-hunk native proposal and 14-case WPT for root's build and browser validation. No source or oracle blocker found. This is **static approval**, not a report of reproduced browser failures or a compiled native repair. At the initial source review the seven failures were predictions. Before sealing, root supplied a completed baseline: the separately retained raw results confirm exactly those seven failures and seven controls passing; see the baseline addendum below.

Authenticated repair: FREEZE `d35b20f6df3f41aebec88ae0cde99dc2d9a849ad030c875b46b058888f710191`, INPUTS `36039fdc92c1931b4fb35c9dc5951ec2a6b363ce3f14662ab207aa1b21c7b9d4`, all 28 entries. The 14-entry prior audit was also authenticated and read; its relevant source/spec evidence is retained in the repair closure. No novelty claim is made.

## Exact source boundary

The original complete file is `71a507cba6ed20b40e690c29555844514870530a5bccc74e41459aa12e46d5bc`, matching the previously reviewed formatted summary repair. Candidate is `d7765d0a1de32f85ad7713409398282556078331e7a1b8ecc047d82b1fc789ab`. The sole replacement wraps the existing `references.flags.insert(ReferenceFlags::from_unit(value))` in `matches!(token, Token::Dimension { .. })`.

In `parse_declaration_value_block`, the original shared arm binds decoded text from Ident, AtKeyword, Hash, IDHash, UnquotedUrl and Dimension. Only the last category contains a numeric dimension unit. The guard therefore removes false unit classification from the first five variants while passing exactly the same decoded unit into exactly the same classifier for every real Dimension.

The arm remains shared. All subsequent U+FFFD/EOF-backslash repair, unquoted-URL closing repair, token/source slicing and first/last serialization metadata are unchanged. The new discriminant test uses the same borrowed-token pattern already used by `is_unquoted_url` in this arm. It introduces no parser calls, mutable provider interaction or allocation. This is a source reasoning conclusion; no Rust type check or performance benchmark was performed here.

The replacement leaves every other original byte intact, including the resolved-output scanner and its two persistence sinks, namespace handling, graph traversal, var/env/attr discovery, recursive nested-block handling and fallback flag propagation. This is a distinct original-parser repair. It neither changes nor adjudicates syntactic relative dimensions in unused fallbacks.

Actual em/lh/rem/rlh dimensions, escaped unit dimensions and every other classifier arm are unchanged by the predicate: the guard is true for all Dimension tokens. The direct 1em cycle WPT is a runtime control for that source argument; it is not exhaustive runtime coverage of all unit classes or graph histories.

## WPT oracle

WPT SHA-256: `e0ba4d87f55fdcbee68b1f5a8db2f130686e8f3d3331d2f9cbd77c19717924b9`.

All registrations are valid: the mixed custom-ident/length and URL/length registrations have an independent 11px initial value, the identifier-only registration has `fallback`, and all are non-inherited. The tests assign valid arbitrary custom-property token streams; invalidity of @em and #em against a later `<length>` registration does not imply rejection by the original custom-property declaration parser.

| Rows | Independent expected behavior |
| --- | --- |
| em, EM, escaped em, lh in custom-ident/length union | These are identifiers, not dimensions. Preserve the registered identifier (including uppercase EM and decoded escape); using it as font-size is invalid and inherits parent 23px. |
| ordinary identifier and identifier-only em | Confirm ordinary identifier parsing and the absence of a length alternative. Both preserve the identifier and inherit 23px for invalid font-size. |
| Real 1em cycle | Registered length depends on font-size, which references that same property. Registered value defaults to 11px and font-size inherits 23px. |
| Absolute 13px | No relative-unit edge; custom property and font-size both become 13px. |
| Unquoted and quoted URL em | Both resolve the same relative URL against document.baseURI and remain valid registered URLs. Neither contains a length dimension; font-size rejects the URL and inherits 23px. No attr taint or resource-fetch premise is involved. |
| @em, #em and #ordinary under `<length>` | Typed registration rejects each and supplies its initial 11px. That valid computed value can set font-size to 11px. A spurious graph cycle instead invalidates font-size and yields inherited 23px, which these rows distinguish. |
| em with fixed 17px font | The valid identifier survives when no font-to-custom reverse edge exists; fixed font-size remains 17px. |

Direct registered-property readback is essential for identifier and URL rows: font-size alone equals 23px both with ordinary type rejection and with a false cycle. Conversely, invalid at-keyword/hash rows need the font-size assertion because the registered result is 11px in both paths. The test includes both observables.

The hash witness is specifically IDHash `#em`; CSS lexical rules do not classify that spelling as unrestricted Hash. The guard also covers Hash as part of the shared source arm, but the WPT does not claim an additional reachable unit-spelled unrestricted-Hash witness. Escaping the identifier does not convert it into a Dimension. Root-relative unit normalization is untouched.

The explicit parent font is independent of default font metrics. CSSOM pixel values avoid platform rendering tolerances. Each fixture is removed through cleanup. URL serialization uses a computed absolute URL and no image-consuming property; `<url> | <length>` ensures URL validity rather than treating a URL as an invalid registered value.

The source/spec oracle is sound: numeric dimensions require a number and unit, whereas custom identifiers and URL tokens remain distinct categories. Registered syntax is checked at computed-value time and registered computed values are substituted into consuming properties. The relative-unit cycle rule cannot turn bare identifier or URL text into a dimension. [CSS Values dimensions](https://drafts.csswg.org/css-values-4/#dimensions), [custom identifiers](https://drafts.csswg.org/css-values-4/#custom-idents), [registered dependency cycles](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles). Complete current primary captures and retrieval metadata are retained under `input/evidence/spec/`.

## Optional parser fixture

The optional child-module fixture calls the real private declaration parser and has 18 token/flag examples plus three EOF escape/URL repair checks. Its `1em` followed by a trailing backslash intentionally decodes a non-unit suffix containing U+FFFD, so empty flags plus emitted repair text are correct. `url(em` must still gain its closing parenthesis while losing the false font flag.

This fixture is uncompiled, unintegrated, and excluded from the native/WPT patch. Its existence is not test execution or proof that the currently indexed old style-unit harness can compile it. No broader harness work is needed to give this narrow static approval.

## Verification and remaining gates

The independent static replay authenticated the imported closure, checked the exact sole replacement, verified preservation of all other bytes, applied/reversed the combined native+WPT patch in a temporary artifact tree, compared exact resulting files, and passed Node's JavaScript syntax check. Fresh relocated replay and tamper rejection are recorded in `CHECK-RESULT.json`.

Root owns observed baseline/candidate browser results, native compilation, lint/format and final commit packaging. Neither a finite WPT pass nor this three-line guard supplies universal tokenizer, SCC or CSS correctness. Existing real-cycle regressions remain useful gates. No live source, WPT, Git, build or browser operation was performed by this reviewer.

Replay after authenticating the review seal: `python3 artifacts/css-unit-token-classification-independent-v1/check.py`.

## Root baseline received before sealing

The root-owned baseline completed with 7 FAIL / 7 PASS / 1 OK in the exact new WPT, plus 227 prior checks passing. I read the raw test-status messages: em/EM/escaped-em/lh and url(em) incorrectly return registered 11px; @em/#em incorrectly leave font-size at inherited 23px. The remaining seven rows pass, including the real 1em cycle. The baseline receipt records 39 stable input pins, including original source `71a507…` and WPT `e0ba4d…`; the full receipt/raw log and extracted review are retained under `baseline/`. Candidate runtime acceptance is still pending and is not inferred from this source approval.
