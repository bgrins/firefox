# v1 replay working directory correction

The v1 kernel source/results are unchanged. Its optional fresh-replay command
ran Lean with the external output directory as cwd. Lean rejects an input source
outside its root, so that command failed before elaboration. The independent
review retains the failure. A manifest-only verifier PASS did not exercise this
branch and must not be reported as a successful fresh replay.

This v2 changes the compiler cwd to the authenticated source directory while
keeping outputs and LEAN_PATH in the fresh external directory. The command
receipt now records that actual cwd. Exact theorem source and audit roster bytes
are unchanged. v1 remains immutable as a historical artifact; use v2 to replay.
