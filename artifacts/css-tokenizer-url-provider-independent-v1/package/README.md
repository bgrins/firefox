# URL tokenizer provider component

Artifact-only Lean model and exact-source Rust replay for cssparser URL, bad-URL and quoted `url()` delegation. No Firefox patch or WPT is included.

Authenticate the external `FREEZE.json` hash supplied with the handoff, then:

```
python3 -I -S check.py
python3 -I -S check.py --run --output /absolute/new/output-directory
```

The checker authenticates every source before executing helpers or compilers. It requires the pinned local Lean, Rust and Cargo binaries in `TOOLCHAIN.json`; all Rust crate sources are included, and Cargo runs offline with the retained lock. Outputs are confined to the new directory, which must be outside the sealed input root. The exact input roster rejects extra files, directories, symlinks, path escapes and duplicate seal/manifest JSON keys. Python children also use isolated/no-site mode, with Python/Lean environment overrides removed. No browser, Mach, network or Git operation is performed.

Read `REPORT.md` and `SOURCE-ADMISSION.md` before interpreting the proofs. This is a universal model component with bounded full-source correspondence. It does not close whole-tokenizer, public-parser-history, native heap/codec or compiler verification.
