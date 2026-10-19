# Parser wrapper history component

Authenticate the externally supplied FREEZE.json, MANIFEST.json and check.py hashes before execution. Copy exactly the manifest-listed closure plus those two seal files to a clean source directory. Then:

```
python3 -I -S /absolute/capsule/check.py --run --output /absolute/new-output
```

The checker rejects unlisted files/directories, symlinks, path escapes and duplicate JSON keys before helper execution or output creation. It authenticates both predecessor capsules, unchanged source/dependencies and tool binaries. It recompiles all Lean modules and standard-axiom audits, executes semantic model mutations, compiles the complete Rust crate in debug/release and for native mutations, and compares exact ordered snapshots with the independently executed model. The trace checker rejects missing, duplicate, reordered, unknown, extra-field and absent/empty annotation corruptions.

Pinned Lean/Rust tool binaries are external dependencies recorded in TOOLCHAIN.json; shared installations are not modified. Generated output stays outside this sealed source directory. No browser, Firefox/Mach build, native/WPT edit or Git operation is included.

REPORT.md and SOURCE-ADMISSION.md define the exact model/native-finite boundary. Source-only replay is not whole-parser verification.
