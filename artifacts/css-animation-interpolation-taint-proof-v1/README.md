# Interpolation provenance component

See REPORT.md for conditional scope. After authenticating published pins:

```
python3 -I check.py --out /tmp/interpolation-provenance-fresh
```

The output directory must not exist and must be outside this capsule. No Firefox build/browser or network access is used. Trusted local Lean and Rust tool paths are recorded in TOOLS.json. All owned executable inputs are covered by MANIFEST.json.
