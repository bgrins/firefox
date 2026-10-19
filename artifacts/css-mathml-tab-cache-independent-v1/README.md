# MathML tab-cache independent review

Read REPORT.md for the review conclusion and its native/provider limits. This capsule includes complete authenticated producer sources, independent static branch checks, retained root WPT pair evidence, and a ten-case follow-up proposal. The follow-up proposal was not run by this reviewer.

After authenticating MANIFEST.json and check.py against the externally supplied hashes, replay with:

```sh
python3 -I -S -B check.py --manifest-sha <external manifest SHA256>
```

The checker authenticates every listed file before loading local review code. It performs no network access, compilation, browser execution, or production-tree access. It can run from a copied directory. The source-bound branch model is a finite control-flow audit, not a Lean proof or a C++ semantic verifier. Root's preserved runtime logs are evidence inputs, not regenerated runtime output.
