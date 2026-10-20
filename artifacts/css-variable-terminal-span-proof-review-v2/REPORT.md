# Terminal-span v2 independent delta review

Verdict: accepted within the predecessor mathematical and source-admission scope. This supersedes the v1 integrity withholding; it does not extend the theorem boundary.

Independently authenticated the externally supplied FREEZE, MANIFEST and checker hashes. Compared both manifests and bytes: all 16 non-checker predecessor inputs are unchanged. The sole changed predecessor input moves the execution-mode guard before imports other than builtin sys. The new integrity runner and delta receipt do not alter mathematics or native source.

Fresh manifest-only relocated replay passed 37 kernel audit results, 10 source bindings, and five compiled Lean model mutation witnesses. The 23 independent kernel boundary challenges from the v1 review passed unchanged; the native serialization-class inventory still matches all 24 modeled non-Nothing classes. Twelve integrity controls rejected before output. The independently reconstructed local json.py shadow no longer executes: the explicit mode guard rejects first. -O/-OO, nonisolated and site-enabled runs are rejected.

The v1 substantive review remains applicable: exact maximal terminal whitespace tokens differ from escaped whitespace bytes; comments and outer-block classes are retained; CRLF uses raw byte lengths; old standalone leading overlap is a byte result only; EOF compatibility and tokenizer/source translation remain admitted. No general retokenization or backslash/newline preservation theorem is claimed. The five mutants are Lean model operations, not Rust-native mutants.

Reproduce with `python3 -I -S recheck.py --output ABSENT_EXTERNAL_DIRECTORY`. Exact command receipts and negative results are under verification/. No production, Git, browser or Firefox build actions occurred.
