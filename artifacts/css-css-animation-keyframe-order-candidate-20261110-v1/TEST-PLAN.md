# Bounded runtime plan

Do not execute from this capsule. Root owns installation, builds, testing, and restoration. Freeze exact inputs before any experiment; record current HEAD separately from this source pin if intervening commits contain research only.

Use the retained browser containing accepted clip fix 171 as the baseline. Snapshot extraction was only a reversible preservation experiment; it is not required by this candidate. Before using the binary, verify its retained receipt and source linkage. Install the same modified WPT bytes in baseline and candidate so the new control and strengthened declaration oracle are identical.

The core inventory is these five WPT pages, run headlessly with the normal process-isolated runner and complete raw logs:

| Page | Purpose |
|---|---|
| `css/css-animations/KeyframeEffect-getKeyframes.tentative.html` | Existing API grouping matrix plus strengthened known-bug case and new interior/logical override case. |
| `scroll-animations/css/merge-timeline-offset-keyframes.html` | Existing percentage/range merging and ordering controls. |
| `scroll-animations/css/timeline-offset-in-keyframe-change-timeline.tentative.html` | Rebinding a timeline must preserve keyframe handling. |
| `scroll-animations/css/timeline-offset-keyframes-with-document-timeline.html` | Unsupported range offsets and ordinary percentage frames. |
| `scroll-animations/css/timeline-offset-keyframes-zero-length-attachment-range.html` | Zero attachment-range boundaries with generated frames. |

The preceding snapshot baseline measured 32 callbacks (29 PASS, 3 FAIL) on the unmodified getKeyframes page and six PASS callbacks across the four range pages. These are historical observations, not a substitute for the new baseline. With this candidate test page, the bounded prediction is 33 getKeyframes callbacks: baseline 29 PASS/4 FAIL, candidate 31 PASS/2 FAIL; the range controls remain six PASS. All five core harness endings must remain OK. Stop for review if the actual baseline differs; do not invent metadata exceptions.

Expected improvements, identified by exact callback name:

1. `KeyframeEffect.getKeyframes() returns expected frames for an animation with multiple keyframes for the same time and with different easing functions and composite operations`
2. `KeyframeEffect.getKeyframes() orders merged percentage groups by their first occurrence while later logical declarations win`

Compare records using kind-tagged callback/harness keys and reject duplicate keys. Preserve exact messages and statuses for all unchanged callbacks. A nonzero WPT process code requires inspection: the baseline deliberately contains an unannotated new failure, while unchanged metadata makes the original case an unexpected PASS on the candidate. Remove its metadata only for final delivery. Harness crashes, malformed lifecycle, missing callbacks, and generic infrastructure errors are not acceptable expected failures.

Candidate mode applies only the two native file edits plus the common WPT bytes with baseline metadata unchanged, performs `./mach build binaries -j6` with a bounded timeout (2400 seconds is the existing local convention), pins the sampled binary/source hashes, and reruns the exact same pages. Capture build diagnostics and raw statuses. Restore source, complete application bundle, build extras, fixtures, and process state even when build/test/comparison fails. Separate baseline and candidate result directories; never overwrite evidence from either run.

Before delivery, run WPT lint for the modified existing page and validate the exact metadata removal. Avoid adding metadata for the new test in the delivery patch. No broad CSS suite or new performance benchmark is required for this first bounded preservation check; no broad performance claim follows from it.

## Root-selected preservation inventory

The root wrapper reuses nine existing pages from the signed snapshot runner, excluding only the two temporary missing-pseudo fixture pages. In addition to the five core pages above, it includes `web-animations/interfaces/KeyframeEffect/target.html`, `css/css-animations/KeyframeEffect-setKeyframes.tentative.html`, `css/css-animations/CSSAnimation-effect.tentative.html`, and `css/css-animations/keyframe-attribute-mutation.html`. This preserves target/JS override behavior and the twelve attribute-dependency controls without a new fixture. No further pages are requested.

Both modes install the exact strengthened WPT; native files change only in candidate mode. Keep baseline metadata unchanged during both modes, and compare actual callback statuses rather than treating unexpected PASS as a semantic regression. Root's predicted inventory is 86 callbacks plus nine OK harness endings (95 kind-tagged records), with exactly the two named FAIL-to-PASS improvements. All other statuses and messages must match. The runtime wrapper must pin these additional page/script inputs separately; this source capsule's five-page pins are not a claim to authenticate the full runtime closure.
