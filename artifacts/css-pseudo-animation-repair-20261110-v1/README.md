# Pseudo-animation repair prerequisites

Research and regression-test preparation for known bug 1615083. No native candidate is included yet.

## Prior work changes the repair requirements

Attachment 9131315 points to Boris Chiou's [D65652](https://phabricator.services.mozilla.com/D65652), retained with its full review discussion. The revision remains Changes Planned. It threads an explicit pseudo target through animation-rule retrieval, includes those rules in pseudo matching and refreshes cascade results for a target without a generated element.

The review reports two unresolved problems: implicit keyframes did not work, and the pseudo-matching change produced unexpected transform-layer hints in broader tests. It also raises target-identity handling for nested pseudos and recommends limiting the new pseudo-specific API instead of widening every ordinary animation-rule caller. These are historical review observations, not failures of a current port; no such port has been built here.

The next design must distinguish lazy computed-style resolution from ordinary pseudo traversal, supply the correct unanimated underlying style, and maintain effect-property freshness without recursively asking for the same animated style. Passing only the six existing explicit-endpoint target-switch cases is insufficient. The companion current-source design review is investigating those exact boundaries before native changes.

## New local regression baseline

`pseudo-animation-underlying.html` adds nine synchronous WPT callbacks. Each animation is paused at 50% and its target, pseudo and computed progress are checked. Generated and non-generated subjects share the same authored style and keyframes.

| Case | Generated pseudo | Non-generated pseudo |
| --- | --- | --- |
| Implicit starting endpoint, 10px underlying to 100px | PASS: 55px | FAIL: 10px rather than 55px |
| Change underlying value to 20px at the same progress | PASS: 60px | FAIL: 20px rather than 60px |
| Important 30px declaration over explicit animation | PASS | PASS |
| Cancel after a computed-style read | PASS: underlying 10px | PASS: underlying 10px |

The ninth callback reads a transform animation before content exists, creates generated content, then removes it. The generated phase passes at translateX(50px); the first non-generated assertion fails with `none`. All three reads execute before assertions, but the later removal assertion is not reached after the failure, so this run does not establish that assertion's result. The test also exercises the sequence implicated by the older transform-hint concern, without claiming a new crash or reproducing that historical assertion.

Overall result: six PASS, three FAIL, harness OK, WPT command exit 1. These failures extend coverage of the known missing-composition issue; they are not three new defects. The exact fixture passes Firefox's WPT linter (LINT.json). No expected-failure metadata was installed for it.

## Evidence and restoration

The browser is the same retained #170 build used by `css-pseudo-animation-admission-20261110-v1`, with its exact binary hashes required by the runner. No rebuild occurred. `baseline1` contains raw events, callback results, terminal process/command receipts, application inventory and restoration records. The temporary WPT and any backup are removed; metadata remained absent. Root independently checked full application/auxiliary inventories and the retained build's recorded binary/source hashes after the run. `ROOT-RESTORATION.json` records that check; the runner checked HEAD/index restoration before later research commits.

`ATTACHMENT-SOURCE.json` authenticates the public attachment response and decoded revision link. `D65652.md` is the Mozilla connector's revision/diff/comment response. These are retained prior-art evidence, not changes applied to the branch. `RUNNER-ORIGIN.json` identifies the earlier local browser wrapper and scoped adaptation.

The final repair must keep native source plus necessary WPT/expectation changes in its own commit. This prerequisite commit carries only the research, prepared fixture and baseline. The 169-entry repair count is unchanged.
