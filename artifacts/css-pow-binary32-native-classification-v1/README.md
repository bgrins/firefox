# Exhaustive host check of pow operand predicates

The optimized Rust executable visits all 4,294,967,296 binary32 encodings.
For each input it compares `is_nan`, `is_infinite` and `abs() == 1.0` with the
three magnitude-bit predicates proved in the Lean companion. `black_box`
separates the float input from the expected bit comparisons. Every comparison
passed in run 2, taking about 6.7 seconds on this host. This duration is an
execution record, not a benchmark result.

This is exhaustive empirical evidence for the three unary predicates under
the recorded host Rust compiler, target and optimization flags. It is not
exhaustive testing of pairs, `powf`, the browser or other platforms, and is
not a formal proof of the compiler or compiled Stylo. Binary32 classification
in the Lean model and this executable use the same documented encoding; their
agreement does not prove the CSS specification was transcribed correctly.

Run 1 mistakenly resolved the rustc launcher symlink to rustup, losing the
argv-name dispatch and failing before compilation. Run 2 locates the active
toolchain through `rustc --print sysroot` and invokes its actual compiler.
The failure logs remain. Compiler version, compiler and executable hashes,
source hash, commands, exit statuses and timings are saved. Temporary binaries
are removed, and no native source, browser application or Git state changes.

Replay: `python3 -I -S -B artifacts/css-pow-binary32-native-classification-v1/run.py run-3`.
The Lean companion is `artifacts/css-pow-binary32-classification-v1`.
