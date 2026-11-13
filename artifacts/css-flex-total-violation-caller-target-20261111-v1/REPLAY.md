# Replay

Run from the Firefox repository root, choosing a fresh output directory:

```
python3 -I -B artifacts/css-flex-total-violation-caller-target-20261111-v1/check.py --out artifacts/css-flex-total-violation-caller-target-20261111-v1/reviewer-replay
```

The checker copies only the seven source modules into owned scratch and uses pinned Lean 4.35.0-rc4 with one worker, a 1024 MiB Lean allocation limit and a 180-second deadline per module. It authenticates all 7,482 inherited standard-library entries before and after, preserves exact command logs and source copies, verifies the complete axiom roster and seven diagnostic lines, and deletes compiled scratch only after observed owned process-group absence. The allocation flag is Lean's internal limit, not an OS-wide process-tree memory cap. Pinned compiler children are assumed to stay in the owned group.

`--modules` is a development-only partial elaboration mode; it does not establish the full audit/control result. A full PASS means target definitions elaborate and the three finite history witnesses check. It does not prove UniversalTarget. No native compiler, browser, or extractor runs.
