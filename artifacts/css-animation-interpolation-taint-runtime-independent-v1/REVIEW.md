# Independent paired runtime and packaging review

**Bounded runtime evidence accepted.** Independent raw parsing reconstructs the joined baseline of 248 PASS / 5 FAIL and candidate 253 PASS / 16 harness OK. Exactly five status improvements match the independently enumerated expected identities: clean-to-tainted bundle samples at .25/.75/1 in the 40-case diagnostic, and .25/.75 in the 24-case landing fixture. The focused baseline's exact 24-name roster was checked. All five original failures reached the URL observer assertion.

## Pair scope

This is a joined baseline, not a newly built 253-case original run. Its constituent raw logs contain 189 prior fix79 candidate subtests, 40 original interpolation diagnostic subtests, and 24 fresh focused baseline subtests. Each retained raw log has exactly one suite start/end, unique subtest and harness identities, and matches its receipt. The candidate has the exact union of 253 subtest identities and 16 harness identities. Shared earlier source/binary pins equal the focused baseline pins.

The 66-entry pre/post pin roster changes only value.rs and the Firefox/XUL binaries. Candidate source is the reviewed `485c097931bcb385bc0ada6679c3429f6f300ffae5f03c75268458feb3316fa0`. Candidate build, scoped format and candidate WPT each exit 0; fresh focused baseline exits 1 with its two expected defects. Stability receipts and the driver's actual comparisons were inspected. This is bounded source/build correspondence, not complete source/configuration/resource or platform closure. The supplemental pin explicitly says its support-file closure is incomplete.

The other 248 statuses remain PASS. That does not establish equality of every internal or rendered observation; notably two diagnostic boundary tests intentionally permit either taint policy. There is no isolated upstream-base runtime claim.

## Final artifact transfer and packaging

The tested landing HTML SHA is `c48a34cac0e4afce1bc52fb6f0614db057c0150a63e771863fe655705a6313e4`. Final SHA `5d4b616f048f17ac8a7cd1bdc56b15a4a7854eb20333fdfc52f6d33203dcf2cd` is exactly one help-link fragment replacement. No JS, CSS or assertions change; the final bytes were not rerun here. The corrected anchor was independently verified in the primary snapshot during the preceding oracle review.

Both final patches contain exactly value.rs plus the landing WPT. Their hashes match root PACKAGING.json. Independent artifact-only patch application and reversal on retained branch/upstream source snapshots reproduced every expected file byte and exact path roster (four operations), then removed the scratch trees. The native change remains one OR expression. Root's Git-tree/index validation is retained as external evidence; this reviewer did not run Git.

## Reproduction and retained limits

`review.py` is the exact root-workspace validator run for this review, including source capture, raw joins and apply/reverse checks; it requires the named original artifact packages. `evidence/` retains the inspected receipts, raw logs, driver, final patches and HTML. `check.py` checks this review's integrity only; it does not rerun browsers, builds or Git. Source/prerequisite approval remains in the separate frozen native-independent package. Formal refinement remains a separate pending review. Lint is root-owned and is not certified by this receipt.

Generated apply-check trees were removed after each run; the final run removed 56,658 bytes. No build targets or browser processes were created. No live source, WPT or Git state was changed.
