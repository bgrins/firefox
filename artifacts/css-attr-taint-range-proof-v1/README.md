# Half-open taint range intersection

This component proves that the proposed max/min predicate returns true exactly
when two natural-number byte intervals share a byte. Fourteen audited results
cover symmetry, emptiness, touching and separated intervals, nonempty containment,
finite taint lists, translation, and counterexamples to inclusive and naive strict
pairwise comparisons. No well-formedness assumption is needed for the predicate
theorem: an inverted interval contains no byte.

The native snapshots come from the independently retained range repair proposal.
The checker requires their sole difference to be the proposed overlap expression.
It extracts the unchanged complete method from each snapshot and compiles it
with a `Vec` adapter. A byte-membership oracle checks 441 finite interval pairs;
the original has 146 mismatches and the candidate has none. Five additional
machine-boundary examples check empty, touching and genuine overlap cases.
These executions are finite evidence, separate from the universal Lean proof.

Authenticate the external FREEZE, MANIFEST and checker hashes before execution:

```
python3 -I -S /absolute/capsule/check.py /absolute/fresh/external/output
```

Inputs must match the closed manifest. The checker pins the Lean executable and
installed Lean libraries, and the resolved Rust compiler executable and version.
Rust standard libraries, the system linker/runtime and compiler correctness are
trusted external dependencies; the extracted adapter is not a verified SmallVec
translation. Output contains generated objects/executables, command logs and
CHECK.json. Keep logs and CHECK.json before deleting completed generated outputs.

## Native and specification boundary

`AttrTaintedRange` documents an inclusive start and exclusive end with `usize`
coordinates. Min/max and order comparison perform no addition or subtraction.
The mathematical bridge interprets admitted machine offsets as natural numbers;
this package does not prove Rust compilation or representation refinement.

The byte-set specification describes this helper's documented range contract.
It does not establish the CSS-to-byte-range producer contract. Actual CSS token
serialization, inserted separators, parser start/end positions, selected fallback
behavior, whole-substitution taint and URL parsing remain separately reviewed
native obligations. Empty byte ranges contain no bytes; this patch does not clear
the boolean taint attached to an entire computed value or substitution.

The separate source review and browser tests must establish that the observed
adjacent URL/resolution case reaches these ranges and that genuinely tainted URLs
remain rejected. No whole-CSS, full native pipeline, performance, novelty or
isolated-upstream runtime claim is made by this proof capsule.
