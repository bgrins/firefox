# Independent parser wrapper-history review

Read REVIEW.md for the precise verdict, evidence and remaining admissions.

Recheck source-only retained evidence:

```sh
python3 -I -S /absolute/path/to/css-parser-wrapper-history-independent-v1/check.py
```

Repeat full producer replay from the manifest-only relocation:

```sh
python3 -I -S /absolute/path/to/css-parser-wrapper-history-independent-v1/relocated/check.py --run --output /unused/external/output
```

The latter needs the exact pinned Lean/Rust tool paths in relocated/TOOLCHAIN.json and creates generated outputs only in the requested directory. No live native sources, Firefox build, Git or browser is needed. Review check.py requires only Python standard library. Authenticate externally supplied FREEZE/MANIFEST/checker pins before executing either checker.
