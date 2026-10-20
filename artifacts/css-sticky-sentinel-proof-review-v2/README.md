# Geometric sentinel v2 independent review

Verdict: **HOLD for the original full formal contract**. See REPORT.md and VERDICT.json. Existing algebra, finite native calibration and integrity controls pass; actual indexed continuation and executed-machine joins remain required.

Authenticate FILES.json with the externally supplied digest before using code, then run:

```sh
python3 -I -S /absolute/review/check.py --manifest-sha REVIEW_FILES_SHA
python3 -I -S /absolute/review/relocated-capsule/check.py --manifest-sha 3c22b32c3840977fcb195a5aa0eb28e1e324417014b027a8140a87c8ff4c5cee --output /new/external/replay
python3 -I -S /absolute/review/run_challenges.py /new/external/challenges
```

`check.py` authenticates receipts, not a replacement for fresh execution. The retained replay completed before its 11 native binaries were removed. All source, raw observations, dependency reports and compilation logs remain. `review_controls.py` documents and executes the negative controls; to repeat it, copy the authenticated review to a disposable directory and remove that copy's existing guard/axiom output receipts first. Frozen originals must remain unchanged.
