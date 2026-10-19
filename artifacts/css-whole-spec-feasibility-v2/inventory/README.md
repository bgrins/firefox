# Whole CSS inventory research, v2

Read `REPORT.md`, then `ledger-slice.json`. This extends the earlier inventory with a concrete source/requirement/dependency/coverage schema and 19 worked records. It is not a complete specification inventory or a proof package.

Authenticate `FREEZE.json`, `MANIFEST.json` and `check.py` against the externally supplied hashes before executing. Then:

```sh
python3 -I -S artifacts/css-whole-spec-feasibility-v2/inventory/check.py
```

The checker authenticates the closed source roster and validates IDs, dependencies, exact local coverage-record copies and retained Lean-source hashes. It does not compile Lean or prove normative interpretation. Web receipts contain rendered excerpts and metadata; full raw source acquisition remains a concrete next task.
