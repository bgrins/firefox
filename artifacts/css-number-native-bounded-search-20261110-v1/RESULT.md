# Bounded native numeric search result

The run passed all 8,942 cases: 26,826 public-token observations and 13,413 lexical comparisons against execution of the actual Lean-decoded numeric document. No mismatch or new native bug was found. All 51 commands exited zero; their retained stdout/stderr hashes were rechecked after the run.

Both default-feature native binaries were built in distinct fresh target directories. The 44 Lean runtime dependency modules were compiled cold, with compiler output matching the accepted bridge replay. The Python comparator and exact JSON type checker were reused unchanged. Every case completed the applicable cache/reset/suffix history, including the UTF-8 comment prefix in history cases.

All temporary source, compiled Lean and native target directories were removed, and recorded scratch/binary paths are absent. This result extends bounded lexical coverage; it does not prove floating-point rounding, full Gecko build equivalence or universal native refinement. No Firefox source, application, canonical library or Git state changed. Independent review has not yet been completed for this expanded run.
