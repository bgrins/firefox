# CSS compensated-exponent repair

The numeric tokenizer can lose an intermediate coefficient or exponent factor even when the complete literal is representable. The repair reparses long numeric prefixes or nonfinite computed values using Rust's complete-prefix conversion, preserving the existing scan and token metadata.

The local paired browser run changes five failures into passes; all eleven new cases pass and 21 existing checks are unchanged, including four expected failures. The vendored parser was explicitly cleaned, its Rust dependents rebuilt and XUL relinked. All three phases exit 0; Mach progress callbacks still emit the known export-tier KeyError during linking. Source and binary hashes remain stable around each run.

Root and independent extracted-source replays pass 852 cases plus three rejecting mutants. Independent challenges add 504 cases. The 256-byte cutoff has separate rounding-aware rational and closed-form checks under explicit native IEEE, pow and conversion assumptions. This is not a Lean proof or complete numeric correctness claim. The numeric lexical model is being developed separately.

The final guard has measurable cost in the isolated body benchmark: approximately 0.3–0.85ns per token across the measured groups. Measured fractional/exponent overhead was smaller than the first proposal’s in these runs, but neither proposal is performance-neutral. No browser performance estimate follows from that benchmark.

Dedicated WPT lint passes with zero problems. General lint reports an ignored-file warning; the changed numeric function passes rustfmt, while the complete original and candidate share an unrelated preexisting comment-alignment diagnostic.

The native patch contains only tokenizer code, its required vendor checksum and one WPT. The alternate upstream-based patch preserves upstream URL/identifier behavior and independently applies/reverses without earlier local repairs. It has no isolated-base runtime run. Research and validation precede the native commits. Public issue searches do not establish novelty.
