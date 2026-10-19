# Depth-limit recovery source capsule

Read REPORT.md and SOURCE-BINDING.md. Authenticate the external handoff's FREEZE.json and checker hashes, then run:

```sh
python3 artifacts/css-parser-depth-recovery-repair-v1/check.py --output /tmp/css-depth-repair-NEW
```

The output directory must not exist. The checker authenticates the entire input closure before executing helpers. It compiles full original/candidate cssparser and two native mutants, checks the fixed24-row observations, compiles the Lean module and exact theorem axiom inventory, rejects two semantic Lean mutants and syntax-checks the producer-unexecuted browser proposal. It makes no network requests or Firefox builds.

Pinned Rust, Lean and Node executables must be available at TOOLCHAIN.json paths. Compiler products stay in the selected output directory. A relocated capsule requires MANIFEST.json, FREEZE.json and every manifest-listed input. development-build/ is excluded historical scratch. The manifest and FREEZE need an external trust anchor; they cannot authenticate their own origin.
