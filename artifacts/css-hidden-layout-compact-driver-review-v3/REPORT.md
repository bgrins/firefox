# Compact runtime v3 driver delta review

Verdict: **GO for the bounded reversible experiment**, with no must-fix issue found in this delta. No native or performance acceptance.

Authenticated draft: `36bd1d722685a8ab75e5a55240ec191c9f4c0ba330b8eb8eaad3acb06cb37e27` (35 payloads). `CHECKS.json` retains every observed hash. Reviewed full prepare/experiment/WPT scripts, cost runner/cleanup/validator and the v2 delta. No scripts were executed by this review; the ten synthetic hook controls are retained producer evidence, not an independent runtime claim.

## Required joins

- Preparation authenticates all six cost execution inputs, pins the post-signing requested HEAD and empty index, requires prior restoration, and snapshots 21 original/head sources with 26 guards. Exact selected baseline bodies must equal HEAD. Six WPT files retain the 58-key roster; optional traces retain their two-file, 12-key roster.
- Only baseline, principal-only, OOF-only and both run optional costs. Original-key variants and trace phases retain their existing behavior. The WPT wrapper is unchanged and still retains unexpected FAIL outcomes while requiring exact complete rosters and stable pins.
- The parent pins guarded sources, both browser binaries and WPT resources before and after timing. The runner's complete before/after dictionaries must equal the parent-constructed dictionary, including all six cost inputs. Parent epoch/source checks and payload reauthentication follow execution, preventing a self-consistent changed runner/fixture from silently passing the join.
- Successful timing requires one observation, no runner failure, independent validator execution and exact agreement with SUMMARY. Full rectangle calibration/observations are validated; mismatches remain measurements, not equivalent-work acceptance.
- Continuing after a nonzero diagnostic exit requires stable identities and verified cleanup: empty top-level and nested error lists, terminal/noLiveGroup true at both levels, removed profile and actual profile absence. Missing receipts, ambiguity or integrity drift throw into restoration. A failed measurement is explicitly recorded as incomplete and does not become successful timing evidence.

## Cleanup and restoration

The cleanup helper records original PID/PGID, initial members and subsequent membership observations. It authenticates the owned leader/session, prefers leader termination, and signals residual groups only with same-user/session/group checks and a surviving known identity. Failed or malformed process scans do not establish absence; permission errors remain errors. Success requires a reaped leader and no live members in the final original-group observation.

This proves no escaped-process absence: a process leaving the original group/session is outside the helper's stated boundary. Process observation/signalling is not an atomic OS transaction. These are disclosed scope limits, not a newly accepted universal process-lifetime guarantee.

The parent catches failures and restores every original source, removes only its installed tests, rebuilds when source changes began, and checks the complete final snapshot and temporary-path absence. A rebuild, restoration, cleanup or integrity failure remains nonzero. No cleanup gate from the prior aborted campaign has been waived.

## Limits

Preparation/execution remain root-owned and require fresh INPUTS binding to the actual post-signing HEAD. This review does not certify a particular future run, make a timing claim, or close native lifecycle/provider obligations. The cost fixture improves diagnostic resolution by separating first/repeat/distinct/second-pass/no-mutation reads and retaining full rectangles, but timer resolution, phase order, small local sampling and non-equivalent work still constrain interpretation.
