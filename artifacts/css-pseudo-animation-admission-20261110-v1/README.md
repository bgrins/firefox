# Non-generated pseudo animation baseline

The current retained Firefox build reproduces all six non-generated-pseudo target-switch failures in the existing KeyframeEffect target WPT. This is known bug 1615083, not a newly discovered defect or a new repair. The bug is open, unassigned and classified S4 in the fresh Mozilla connector response retained as `bug1615083.md`.

## Observed result

The unmodified `web-animations/interfaces/KeyframeEffect/target.html` ran headlessly with the standard WPT configuration. It produced 24 distinct callbacks: 17 PASS, seven expected FAIL, and harness OK. The seventh failure rejects `::placeHOLDER` as an unsupported animation target; it is separate from this investigation. The harness exits zero because these failures already have checked-in expectations, not because all assertions pass.

| Selected pair | Actual result |
| --- | --- |
| Set target first, then ::before, with generated content | PASS: computed margin-left is 50px |
| Same operations without generated content | FAIL: computed margin-left remains 10px instead of 50px |

The other five missing-pseudo failures cover setter ordering and retargeting between originating elements or pseudo selectors. Their exact names, messages and raw events are in `baseline1/TEST-RESULTS.json` and `baseline1/wpt-raw.jsonl`. These are six manifestations of the existing issue, not six new bugs.

The browser is the retained #170 build authenticated by `css-style-query-current-build-20261110-v1/build-result.json`: application BuildID 20261110143843, version 160.0a1, with exact Firefox/XUL/application.ini hashes checked before and after execution. No native rebuild or test edit was needed. This was a local branch build, not an isolated upstream or release-browser comparison.

## Contract and implementation map

[CSSOM getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle) selects the requested pseudo and returns resolved longhand values for the connected target under its stated conditions. [Web Animations' composited-result algorithm](https://drafts.csswg.org/web-animations-1/#applying-the-composited-result) inserts composed effect values into the appropriate cascade origin. The captured specification sections, established WPT and bug discussion support investigating missing animation composition here; this capsule is not a complete formal derivation of pseudo existence or the entire CSSOM algorithm.

| Surface | Inspected behavior |
| --- | --- |
| `style_resolver.rs`, `match_pseudo` | Supplies empty `AnimationDeclarations`; its comment relies on animation handling during ::before/::after traversal. That route cannot supply the missing composition merely by traversing a generated element that does not exist. |
| `EffectCompositor::GetServoAnimationRule` | Reads the target/pseudo EffectSet, sorts effects and composes them. The property-set freshness boundary must be inspected before reusing it from lazy resolution. |
| Existing WPT metadata | Six missing-pseudo expectations cite bug 1615083; raw outcomes reproduce them. Metadata was preserved, not removed to change the harness result. |

Searchfox discovery precedes the two exact local source copies in `source/`; SOURCES.json authenticates those copies against Git revision 5f9cbe5753f81d81c4bfe8b4fc646465042683dd. Searchfox's indexed source is navigation evidence and is not substituted for the locally built revision.

The bug discussion corrects its original restyle-posting hypothesis. In bug 1615083 comments 2–5, the proposed repair belongs in lazy pseudo-style resolution, with fresh animation cascade results. A nonexistent generated element does not require a generated-element restyle merely for CSSOM. Comment 8 records an older proposed patch (attachment 9131315); review that prior work before designing a replacement. This finding is independent of held #160's repeated-drain convergence question.

## Reproduction and restoration

From the Firefox repository root, `python -I -B artifacts/css-pseudo-animation-admission-20261110-v1/run.py <new-output-name>` runs the existing test using the configured Firefox Python path. It requires the pinned retained browser, clean tracked tree, exact test/metadata/harness bytes and adequate space for an application backup. It leaves the test in place and restores the application and three auxiliary build files. The runner's origin and scoped changes are recorded in RUNNER-ORIGIN.json.

The completed baseline has terminal command receipts, no surviving owned process group, and no remaining backup. Root independently rechecked the full application and auxiliary file inventories, all test-input hashes, Git HEAD/index and tracked cleanliness, plus the raw callback counts; see ROOT-RESTORATION.json. Later research commits can advance HEAD without changing this historical execution receipt. The 29 preexisting untracked paths were preserved.

## Next bounded work

Inspect the older patch and current lazy-resolution callers, then prototype animation declaration retrieval for an explicit logical pseudo target with correct effect-property freshness. Keep ordinary traversal, visited styling, generated pseudos, null-target cleanup and retargeting controls intact. Do not fix this by inventing generated content or blindly posting hints to the originating element. Require the six existing failures to pass without worsening the 17 controls; the unrelated placeholder failure is not part of that acceptance criterion. A native repair and any necessary WPT/expectation change must be packaged separately from this research.
