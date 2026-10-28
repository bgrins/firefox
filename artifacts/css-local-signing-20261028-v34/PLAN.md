# Reviewed successor signing sequence

V33 is complete: signed HEAD80cc911cf217a7bd050646b3cb448147c3a32110 and synchronized epoch b50124382a40e3c0001d9237e26517dc34cb9c695afa72d76d172bd62a35c961. The previously staged 165 files belong to that completed historical signing sequence. The new init helper requires exact v33 FINAL/runtime/CURRENT equality and empty staging through the unchanged generic verifier.

Root executes serially:

1. `python3 -I -S -B artifacts/css-local-signing-20261028-v34/init.py`
2. The unchanged `commit.py`, once for each selection in order: extended-counter, line-height, shared-validation, continued-research.
3. `python3 -I -S -B artifacts/css-local-signing-20261028-v34/finish.py`, which signs the evidence checkpoint and performs owned CURRENT-only synchronization after verifying the entire signed chain.

All four research selections are explicit and disjoint: 503 files. No binary backup, target cache, unrelated package, native source or ledger is selected. The fourth group includes the failed/restored paired experiment and newly completed grid/model/audit research. Its raw wrapper failure is preserved; no candidate browser result is manufactured.

Every commit preserves the existing native working diff and full source/binary/research pins. Synchronization reconstructs the expected epoch from the initial state plus exact signed artifact-only receipt files, verifies all parent/tree/signature bindings, preserves the 75 recovery captures and separately checks both untracked installed WPT identities against committed research copies. ROLE/OWNED remain historical and unchanged.

If signing fails, stop with the exact stage preserved and inspect that group's log; do not rerun its staging path blindly. All execution is root-owned. The agents prepared these files without running Git mutations, source writes, builds or browsers.
