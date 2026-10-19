# Replay

Authenticate FREEZE.json and MANIFEST.json against the handoff hashes first. Run:

```
python3 check.py --lean /absolute/path/to/lean --output /absolute/new/output
```

The checker verifies all source inputs before executing imported helpers, repeats the complete component replay, repeats the deliberate shared-codec diagnostic, and verifies a source-tamper rejection before output creation. It requires the pinned Lean 4.35.0-rc4 executable and its existing installation. No native build, network, browser, or live repository change is performed. Generated replay directories and object files are not capsule inputs. REPORT.md defines the acceptance boundary.
