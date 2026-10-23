# Hidden layout cost v2 — unrun additive diagnostic

This preserves v1 and its rejected combined cleanup receipt. No result from v1 is silently accepted as complete, and v2 has not launched Firefox. It adds query-order measurements and changes cleanup observability, not a native repair.

Run only when root authorizes the runtime window:

```
python3 -I -S /absolute/capsule/run.py --binary /absolute/firefox --output /absolute/absent-output --label PHASE --pin /absolute/source
```

Output must be outside the capsule. Keep a copied timing capsule and its output as siblings. Six execution inputs must be pinned: run.py, cleanup.py, validate.py, CONFIG.json, probe.html, benchmark.js. A runtime parent must authenticate those hashes and compare each runner `before` hash to its own source/binary/input hashes, as well as requiring before==after.

## Measurement

The12 configurations (principal/OOF × visible/hidden ×1/32/256 branches), two warmups and seven measured rounds remain. Each branch has three nested levels. An independent visible peer calibrates full rectangles at160/168px widths before measured target work. OOF centers change x76↔80; principal flex-start coordinates are8×index. Initial visible target rectangles must also match. Peers are removed before the target is hidden and timings start.

Each of16 recovery iterations mutates width and flushes the outer container, then records first query, same-leaf immediate repeat, other selected leaves, and a second full pass. Another16 full passes occur with no mutation or outer query. Each bucket retains per-iteration times and each read retains its identity/full rectangle. Default total:84 measured batches and13,440 reads. With one branch, the distinct bucket performs zero reads; its timing is harness overhead, not layout work. Construction now includes a calibration peer, so absolute timings are not identical-work comparisons to v1.

Geometry differences remain diagnostics in SUMMARY; visible calibration failure, missing reads and invalid receipts fail validation. Timing medians are sums per batch, not evidence of native reflow counts. Repeated forcing needs the split result or a separate source-bound trace. The old34 principal improvements include position/ancestor/anonymous cases and cannot be reduced to zero-output cache misses.

## Cleanup boundary

SPAWN.json is written immediately after launch, with PID and expected PGID from start_new_session, then updated with observed group members. `/bin/ps` supplies only numeric identity/state and birth fields; only rows matching the saved PGID are retained. POSIX `getpgid`/`getsid` confirm ownership rather than treating macOS `ps sess` as a session ID. No process command lines are collected.

Cleanup first terminates the owned leader and waits up to5seconds. If live original-group members remain, their UID/session/group must match and a previously observed PID/birth identity must survive before any group signal. Only then is TERM sent; KILL is conditional on a subsequent live-member check. A departed group gets no signal. EPERM and inspection failures remain failures, not successful cleanup. Group PID reuse without an authenticated survivor is refused. Signals and waits, including failed cleanup and final inspection, are retained in RESULT.

The independent source review found that silently skipping malformed ps rows could falsely establish absence. The corrected parser rejects malformed nonblank rows, nonnumeric identities and an empty listing; three mocked rejection cases are retained in SYNTHETIC.json.

`terminal` requires leader exit/reap, no live members in the original group, and no cleanup error. Zombies are recorded but are not executing/live members; arbitrary non-child zombies cannot be reaped by this runner. This does **not** establish absence of descendants that deliberately escape the original process group/session. The runner does not signal unrelated groups. Final observation is not a race-free operating-system lifetime proof.

The browser receipt deadline is75seconds, fixture deadline45seconds, followed by bounded waits/inspections. Each ps invocation has a3second timeout. This tool is a diagnostic runner, not a sandbox. Profile deletion is independent evidence and cannot substitute for the terminal/noLiveGroup checks.

A parent may keep a nonzero calibration/deadline result as diagnostic and continue only when resource hashes match, cleanupErrors is empty, termination.terminal and noLiveGroup are true, the leader exit is non-null, and the profile is actually absent. Missing cleanup evidence or source/binary drift must fail the experiment's integrity gate. No claim that all escaped processes are absent should be inferred from these fields.

## Source-only checks

`python3 -I -S test_tools.py` uses generated observations and mocked process operations only. It checks84/13440 completeness, wrong visible-position rejection, missing-read rejection, retained target-position mismatches, graceful departure, verified remaining-child TERM, EPERM refusal, changed-birth group refusal and zombie distinction. Synthetic receipt size is1,320,731bytes under the4MB POST cap. Python sources were parsed without invoking a compiler toolchain. No browser, Gecko build, production edit or Git operation was performed.

PS-FIELDS.json separately checks the platform's ps field parser against the audit Python process's own POSIX PID/group/session, without retaining other members or sending signals. The sandbox blocked the initial ps launch with EPERM; the approved read-only check outside it passed. Actual browser runs therefore need permission to inspect the owned group; missing permission remains a cleanup failure.
