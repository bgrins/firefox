# CSS verification continuation

Executed Chrome comparisons now separate two questions that the earlier candidate conflated. All results use the existing exact fixtures and retain their authored assertions, raw logs, private records and explicit browser settings. These are bounded local-build observations, not claims about every release configuration.

| Observation | Firefox original | Firefox candidate | Chrome for Testing 156.0.8078.80 |
| --- | --- | --- | --- |
| Descendant first reads at depths 1, 2, 4, 8 | Four FAIL | Four FAIL | Four PASS |
| Same-element acyclic opacity | 0.75 | 0.545455 | 0.75 |
| Same-element stepped feedback font | 32 px | 16 px | 32 px |

Literal trajectories and initial calibrations match across engines. Chrome completes each descendant chain on the first read in this fixture. The Firefox candidate only improves later frames at some depths; that is still insufficient. The ranked DAG model and earlier late-Pending trace remain useful, but neither proves native scheduling correctness.

For same-element timing, Chrome agrees with the original Firefox effect outputs while also retaining pre-own-effect computed CSS durations. Firefox original reports different computed CSS durations from its applied timing. The candidate's additional tentative acyclic PASS therefore is not established fix evidence: it changes behavior relative to executed Chrome under an unresolved composed-input oracle. The feedback callback deliberately has no contextual endpoint oracle. Keep computed CSS, applied effect timing and rendered output distinct.

Next implementation work:

1. Target the demonstrated descendant first-read gap. Trace how animation timing updates and output composition become visible before dependent descendant style is published. Preserve all four first-read assertions; do not replace them with later-frame checks or a fixed number of passes.
2. Resolve the timing-input contract separately. Executed Chrome and the prior Blink/WebKit source review support investigating pre-own-effect timing, but do not by themselves settle the normative specification. A controlled prototype must separate timing inputs from keyframe/effect inputs, handle root-unit caches and invalidation explicitly, and preserve or intentionally justify same-element behavior.
3. Bridge native completion to the formal model. Current Pending entries do not record dependency provenance or completed input generations. A sound worklist needs a justified dependency relation, complete notification, evaluation acknowledgement and termination. The reviewed strict-ancestor sketch states the missing inputs and falsifiers; it is not a production fix or a certificate for existing queue data.
4. Publish the completed research, then the already validated min/max and logarithm native/WPT fixes in separate commits when signing is available. V80 ended with a 1Password failure and must not be rerun or bypassed with unsigned commits. Prepare any successor from the actual preserved state and include the new evidence.

V80 signing actual 78873/f67bbe/1 failed with Git 128 and `1Password: failed to fill whole buffer`. Independent root verification 62112/4d56c5/0 confirmed unchanged HEAD/index/canonical state and absence of the temporary index and lock. No new commit is claimed. Both Chrome runs finished, their private processes/profiles are gone, and the verified portable browser/driver/archive directory was removed (607,196,093 regular-file bytes). Final Firefox state verification 20173/5b53c4/0 is unchanged. No experiment browser or signing process remains active.

Accepted native fixes remain 149; canonical Lean counts are unchanged. The 563-path untracked census remains the recorded expected set; project prototypes retain committed recovery copies. [Full work table](WORK-TABLE.md), [descendant comparison](../css-chrome-finite-depth-comparison-v1/README.md), [same-element comparison](../css-chrome-same-element-comparison-v1/README.md), [native completion sketch](../css-contextual-duration-descendant-completion-sketch-v1/README.md), [previous roadmap](../css-continuation-roadmap-20261030-v84/PLAN.md).
