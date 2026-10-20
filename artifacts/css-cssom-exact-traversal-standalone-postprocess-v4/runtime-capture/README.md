# Standalone v4 without the DOMRect repair

Prepared driver, not executed by its author. Root owns review and execution.

The candidate consists of the four sealed traversal-v4 native files plus exact pre-fix-102 DOMRect.cpp from `git show c0e8c7fd1deb^:dom/base/DOMRect.cpp`. The latter is byte-identical to the historical integer-only source snapshot and its recorded runtime hash, `7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5`. Proposal-v4's own original DOMRect is already fixed; it is the restoration role, not the temporary pre102 role.

After source/index/input preflight, the driver installs the unchanged four-case WPT and five candidate files, checks lint/format, runs `mach build binaries`, then runs the same 23-file/74-subtest WPT selection. There is no timing run or baseline rerun. Results must exactly match historical integer-only keyed statuses, expected statuses, file outcomes and exit 1: 70 PASS, four FAIL, of which two are expected failures. It does not normalize the two transformed precision failures into expected passes.

Source roles live under original/ and candidate/. Runtime evidence is written under standalone/, avoiding collision with source snapshots. The finally block restores all five pre-run sources, removes the temporary WPT and rebuilds. Final receipts require fixed native files, HEAD, staged binary diff and full stage entries to remain unchanged. This returns the current fix102 baseline; it does not install the standalone candidate.

The driver permits the pinned 229-file staged research commit, restricted to artifacts outside this directory, without signing or index writes. Its exact staged-content guarantees exclude index stat-cache/flag bytes. No concurrent source, HEAD or index writer may run. GIT_OPTIONAL_LOCKS=0 is inherited by Git and Mach.

Root may inspect without mutations using:

```
python3 -I -S -B artifacts/css-cssom-exact-traversal-standalone-v4/experiment.py --preflight
```

After review, omit `--preflight` to execute and redirect its output to this directory's experiment.log. Assertions are required; never launch with `-O`. INPUTS pins the exact driver, source snapshots, historical oracle and inherited reviewed runtime dependencies. Historical binaries are not replayed or archived here. A passing run would establish only the requested shared-build independence from fix102, not universal upstream/native acceptance.
