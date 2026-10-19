Authenticate the handoff FREEZE.json and MANIFEST.json hashes first, then run:

```
python3 check.py --lean /absolute/path/to/lean --output /absolute/new/output
```

This source-only independent replay verifies the imported integration before running its checker and additionally checks the whole tokenizer source delta. Generated objects and replay outputs are excluded from the source manifest. See REPORT.md for scope.
