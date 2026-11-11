# Combined keyframe repair history

Signed commit `824de5537a87648da355c62fe685db0f18bec9a6` contains the percentage and
named-range repairs for bug 1778402: three native files, three WPT pages and one
metadata file. They remain one catalogue entry, #172. Source/proof/runtime
research precedes this commit. The historical percentage-build catalogue commit
follows it; the current v20 catalogue supersedes that snapshot.

The six original commits above `3d55e8e0d364` became five. The original tip
`526cc18cd58f` remains on `backup-stylo-keyframe-172-20261110`. Every rebuilt commit
is SSH-signed and signature-verified. Original author names, email addresses and
dates are preserved; the combined repair subject is broadened to cover CSS
keyframes. No existing review trailer was present or removed.

`rebuild.py` constructs trees in an isolated index, requiring every original
patch's parent blobs to match before applying it. It verifies each prefix's
non-artifact tree, exact final-tree identity, and unchanged live index and
untracked inventory before atomically updating the branch with an expected-old
reference. It does not reset or check out worktree files. The four research
patches remain byte-identical; all 527 preexisting nonignored untracked paths are
preserved. Owned output paths are explicitly required to be ignored and absent
before construction. This is not a whole-workspace byte inventory.

`RESULT.json`, `AFTER-CHECK.json` and `RANGE-DIFF.txt` record the completed checks.
The skill's churn helper printed its totals and origin attribution, then failed
on an existing shell syntax error. Independent Git numstat checks confirm zero
churn gap before and after; no helper was modified. The separate history-review
capsule independently simulated the 251 touched paths before execution.

Research prefixes have the same native/test tree as the pre-fix base, whose
percentage baseline was tested. The combined native prefix has the exact bytes
tested by the successful range candidate, and the final committed-source build
and focused WPT run are recorded separately in
`css-keyframe-order-combined-current-build-20261110-v1`. Artifact-only later
commits do not change those native inputs. Archived transaction runners retain
their original HEAD/binary guards; they are not rerun on rewritten prefixes.

Frozen old source SHAs and receipts deliberately remain unchanged and reachable
through the backup branch. The earlier v19 catalogue and percentage-only current
build receipt are historical, not statements about the combined build.
