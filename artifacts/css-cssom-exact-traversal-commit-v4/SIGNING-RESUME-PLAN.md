# Resume after the failed first signature

This is an execution plan for the root agent. No signer or Git mutation was run while preparing it.

## Recorded state

HEAD is `99a9ca84f08370c1797720db8688bcb3747f6985`. The failed attempt returned 128 with the same before/after HEAD. All 229 staged blob hashes exactly match `commit-v3/lifecycle-results.json`; signing remains enabled. `SIGNING-RESUME-PREFLIGHT.json` records the staged diff and complete index-entry hashes. This is a historical snapshot: recheck it before resuming, rather than requiring it after successful commits.

Do not rerun `css-signing-resume-20261020-v2/sign-research.py` unchanged. Its first iteration refuses to overwrite the existing `1-recipe.json`. The commit helper also overwrites its per-id message, log, and receipt files. Both hazards occur independently of whether the signer becomes available.

## Resume procedure

1. Reserve a fresh attempt directory. Preserve the failed attempt and helper receipts. Authenticate the five recipe pins and the helper pin in `standalone-evidence-draft.json`, then run `python3 -I -S artifacts/css-cssom-exact-traversal-commit-v4/check-standalone-evidence.py`. Read-only Git commands should use `GIT_OPTIONAL_LOCKS=0` and `git -c core.fsmonitor=false`.
2. Recheck actual HEAD, complete staged entries, staged binary diff, and all 229 staged blob hashes against the preflight snapshot. Require `commit.gpgsign=true`. If these differ, stop for reconciliation; do not reset, unstage, re-add, or silently adopt a new starting HEAD. No source/build task or second signing worker may run concurrently.
3. Create a new finalized copy of the first recipe in the fresh attempt directory, preserving its file roster, hashes, and message. Set only `expected_head` to the verified current HEAD and give its helper `id` an attempt-specific suffix; retain the original id as `base_recipe_id`. This prevents overwriting the earlier helper evidence. Invoke the pinned `commit-item-v2.py` only after root authorization to resume. Its already-staged branch verifies all 229 staged blobs and reuses them without staging again.
4. After each successful invocation, require exit 0, changed HEAD, the exact previous HEAD as the new commit's parent, exact changed-path roster and committed blob hashes, a `gpgsig` header, and an empty index. Retain the new finalized recipe and helper message/log/receipt in the attempt directory immediately. Signature presence is the helper's existing check; it is not an additional claim of independent cryptographic verification.
5. Only then finalize the next recipe against that actual new HEAD. Preserve the five original research recipe order listed below. Append the new standalone evidence recipe as item 6. Do not precompute future commit hashes or rewrite the immutable draft recipes.
6. If a signer or any later check fails, stop before the next item. Record actual HEAD and index hashes. Preserve staged contents and all receipts. A later resume starts at the first incomplete item in a new attempt directory. A recipe file's existence, a log, or a successful-looking receipt alone is insufficient to skip an item: authenticate the actual commit, exact parent, signature presence, changed paths, and blob hashes. If a commit succeeded but receipt writing failed, reconcile that commit before retrying; do not attempt an empty duplicate commit.
7. After all six evidence commits succeed, reauthenticate root acceptance and the five-file patch, then finalize the separate `native-accepted.json` against that new HEAD. The helper's patch branch independently constructs/checks the exact staged tree using a disposable index. This native commit contains four native files and one WPT; no DOMRect fix 102 or research files belong in it. Stop on any native patch, tree, signature, or index mismatch. Do not bypass signing.

## Ordered recipes

| Item | Recipe | Files |
| --- | --- | ---: |
| 1 | `artifacts/css-cssom-exact-traversal-commit-v3/lifecycle-results.json` | 229 |
| 2 | `artifacts/css-cssom-exact-traversal-commit-v3/runtime-results.json` | 276 |
| 3 | `artifacts/css-cssom-exact-traversal-commit-v4/research-source-draft.json` | 693 |
| 4 | `artifacts/css-cssom-exact-traversal-commit-v4/research-runtime-draft.json` | 245 |
| 5 | `artifacts/css-primary-destruction-ownership-refinement-commit-v1/draft.json` | 355 |
| 6 | `artifacts/css-cssom-exact-traversal-commit-v4/standalone-evidence-draft.json` | 179 |
| 7 | `artifacts/css-cssom-exact-traversal-commit-v4/native-accepted.json` | 5 |

The first six recipes have disjoint rosters: 1,977 artifact paths total. Item 6 includes the closed producer capture, both standalone reviews, actual `css-cssom-exact-traversal-acceptance-v4`, and 11 root receipts. The unsealed original standalone directory is deliberately excluded. Five historical sibling inputs already exist byte-identically at the recorded HEAD; all other 400 captured input bindings are covered by these research recipes or retained native/test snapshots.

Recipe/checker/audit/resume-plan metadata is outside these payload rosters to avoid recursive self-pinning. Retain it separately in a management evidence commit if desired; do not silently add it to the exact six recipes or the native patch. Shared mutable ledgers and signing-attempt logs likewise require an explicit later roster.

## Acceptance limits retained

The standalone gate requires the historical 74 keyed subtests and 23 file outcomes, including WPT exit 1: own 4 PASS; separate transformed tests 2 PASS and 2 unexpected FAIL without fix 102; existing tests 64 PASS and 2 expected FAIL. It does not assert all tests pass without fix 102. Qualified performance acceptance retains the possible deep-root-transform cost. No isolated upstream runtime, universal native arithmetic/lifetime proof, or full CSS verification is claimed.
