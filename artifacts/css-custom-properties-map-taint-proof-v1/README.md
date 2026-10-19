# Replay

Authenticate externally supplied FREEZE.json, MANIFEST.json and check.py hashes before executing code. The closed manifest includes all source inputs; FREEZE.json and MANIFEST.json are the two sealing files.

```
python3 -I -S /absolute/capsule/check.py --output /absolute/fresh/external/output
```

The absolute Lean executable in TOOLCHAIN.json and its pinned library inventory must be available. Copying only manifest-listed files plus the two seal files to another directory is supported. No repository source, Firefox build, browser, network or Git is required. Output must be fresh and resolved outside the capsule; generated modules, object files and command logs are external. Keep CHECK.json and logs as replay evidence before removing completed generated targets.

The checker rejects unisolated/optimized Python, modified or extra/missing inputs, symlinks, duplicate JSON keys and unsafe names. External hash authentication remains necessary: a self-consistent malicious replacement of the checker and all seals cannot authenticate itself. Source byte checks are not verified parsing or translation. Read SCOPE.md before applying the theorems to native code.
