# Earliest source positions for keyframe groups

`record_matches_first` proves that updating group metadata while scanning source
entries backward returns the position of each group's first source occurrence.
The reference uses `List.find?`; the executable model uses a reversed left fold
with overwriting updates. `enumerated_input` applies this result to source ordinals
attached by `zipIdx` before reversal. This matches the candidate's
`iter().enumerate().rev()` order.

The model also proves that metadata exists exactly for encountered groups,
unrelated keys retain their metadata, and comparisons or other pure consumers
receive the same metadata as the independent first-occurrence reference. It does
not implement or verify Rust's sorting algorithm.

The native candidate keeps actual group slots unchanged until property
deduplication has consumed its saved indices, updates a parallel position vector,
then sorts owned `(keyframe, position)` pairs. Its separate `Slots.lean` model
checks length alignment, update validity, fresh unique positions and zip length.
These are complementary models, not a mechanically checked coupled simulation
of the Rust arrays and C++ matcher. Native group identity/equality, slot lookup,
ownership, declaration payloads and sorting remain source-reviewed obligations.
In particular, this pointwise map alone does not prove native slot alignment or
that native source positions are unique.

The source/spec trace and current-browser failure are in the sibling
`css-named-range-group-order-review-20261110-v1` and
`css-named-range-group-order-probe-20261110-v1` capsules. This is a possible extension
of existing repair #172 / bug 1778402; it adds no independent browser bug count.

Run:

```sh
python3 -B check.py --lean /path/to/lean --out /new/output/directory
```

`verification/report.json` records 11 kernel theorem/example audits and three
compiling semantic mutants: a forward scan, retaining the first reverse-scan
coordinate, and an off-by-one coordinate. Each mutant compiles, rejects the
unchanged laws, and fails the unchanged concrete witness with a false-proposition
diagnostic. The positive witness succeeds first. Only ordinary Lean logical
axioms are permitted; no `sorryAx` or native-evaluation axiom is accepted.
Fresh temporary compiled outputs are removed after checking.

This capsule does not integrate into the canonical CSS library or claim broader
CSS specification coverage, native memory safety or a verified prose translator.
