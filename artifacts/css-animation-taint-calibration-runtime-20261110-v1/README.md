# Animation-taint fallback calibration

The same four-callback WPT reproduces three current-spec expectation failures
in the local branch browser and installed Nightly 162.0a1 (BuildID
20261109214446). The ordinary-variable control passes in both. This is one
unfixed issue group newly reproduced by this investigation, not three new fixes
or a claim that the issue was previously unknown.

| Case | Local | Installed Nightly | Observed result |
| --- | --- | --- | --- |
| Animated variable in scroll-timeline-name | FAIL | FAIL | --live instead of --fallback |
| Animated variable in timeline-scope | FAIL | FAIL | --live instead of --fallback |
| Never-animated variable | PASS | PASS | --live accepted |
| Inherited animated variable in animation-name | FAIL | FAIL | --live instead of fallback-animation |

Each failing direct case first verifies the animated custom value, source
animation identity, paused state and progress 0.5. The inherited case verifies
its inherited value before failing animation-name; later timeline assertions in
that callback are not reached and are not counted as demonstrated failures.
Both harnesses complete OK. No feedback loop, stale registry, security impact,
release-channel behavior or performance consequence is established here.

The current Variables Level 1 substitution rule rejects animation-tainted values
in nonanimatable destinations and uses an available fallback. The accompanying
source review authenticates this rule and its 2021/2022 history. However,
[CSSWG issue13933](https://github.com/w3c/csswg-drafts/issues/13933) remains open:
it discusses removing inherited taint and the difference between property-name
and value provenance. Thus the inherited expectation follows current text but
is under active design discussion. A production repair must explicitly settle
its acquisition/lifetime contract; this calibration does not silently select
Blink's value-taint policy or prove global-name policy correct.

The source hypothesis and fixture are retained in
../css-animation-timeline-renewal-gates-20261110-v1. Root corrected that report's
function name to get_animated_properties; the pinned excerpt itself was already
correct. Attribute-taint and its URL restrictions are a separate mechanism.

## Execution and restoration

run.py derives from the checked named-timeline transaction with an empty native
source roster and the build step removed. run_installed.py differs only in its
explicit browser path. Four exact callback names are checked. The runner permits
assertion failures as measurements and always restores the saved local browser
and three build extras. No source compilation occurred.

Root independently checked both full-application restorations, Git state,
terminal owned process groups, removed temporary WPT and removed backups. The
installed browser executable, XUL and application metadata hashes are unchanged.
The active objdir is retained. Runtime1 and installed1 receipts bind historical
checkpoint743ad7bca84a; rerunning their HEAD/index audit after later commits is
expected to reject the changed history.

ROOT-COMPARISON.json authenticates the two raw status vectors and exact shared
fixture. The existing browser repair catalogue remains at168 entries; this lead
has no repair commit yet. The next task is the policy-qualified implementation
and formal contract review, before any native patch or additional loop probe.
