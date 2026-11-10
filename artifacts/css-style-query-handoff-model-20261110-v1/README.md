# Style-query handoff model

This Lean model verifies query-mask delivery and certified ancestor marking for
the frozen candidate patch. It proves the finite handoff contract under an
explicit stable-tree assumption. It does not prove native memory safety, queue
completeness, or convergence of successive CSS/animation traversals.

The model's finite tree is the selected traversal subtree. Its root can be below
the DOM root. Every modeled producer and child belongs to that subtree, and each
nonroot parent step strictly decreases a natural-number depth. The executable
ancestor walks therefore use no arbitrary fuel.

The 37 checked laws cover:

* Exact named/unnamed projection and delivery to every eligible immediate child
  of each collected producer, characterized by independent declarative relations.
* Union with existing hints, no invented query bits, preservation of font hints,
  and query collection/projection independent of producer font bits.
* Exact ancestor coverage from the producer through the traversal root, excluding
  that producer’s seeded child from its path; existing dirty state is preserved.
* Early-stop equivalence when certificates are separate from dirty bits and
  certify a complete, dirty ancestor path. Certificate updates preserve that
  invariant across arbitrary finite producer sequences.
* An explicit composition theorem: optimized marking over precisely the active
  producers with eligible children equals the reference handoff's dirty result.

An empty certificate set is sound even if arbitrary native dirty bits are
already set. The proof does not allow those bits to be treated as certificates.
`certify` represents the completed prefix-marking batch; equivalence to individual
Rust HashSet operations and the actual reversed insertion order remains a native
mapping obligation, alongside worker joining, element lifetime, parent/child
identity, eligibility, and queue collection. See `MAPPING.md` for the boundaries.

## Validation

Lean 4.35.0-rc4 checked all 37 laws. The axiom inventory contains only the standard
`propext`, `Quot.sound`, and `Classical.choice`; there are no added axioms or
admitted proofs. Twenty-five executable observations cover branching trees,
styled/unstyled children, masks, old hints, shared paths, repeated producers,
and preexisting dirty state. One explicitly off-domain case demonstrates that
an unsound certificate can miss the root.

Six type-correct mutations are rejected by the unchanged laws and exact false
semantic witnesses: font-only projection, the wrong producer's children,
overwriting old hints, truncating the ancestor path, requiring a font bit, and
using dirty bits as certificates. A seventh control rejects changed candidate
bytes. The certificate witness explicitly unfolds the recursive equation before
`decide`; an arbitrary compile failure or failure to reduce is not accepted.

`SOURCE.json` pins the candidate patch and the source-review baseline manifest.
The patch SHA-256 is
`75ab9dc8feec80bae0ac17a4b3cdf141373372283c2cb6721491dd7ea3993d1b`.
Source-only replay copies exactly nine files into a fresh temporary directory;
all owned compiled output is removed. No live Firefox files, WPTs, canonical Lean
library, build, browser, or Git state are changed by this artifact.

From the Firefox repository root:

```sh
python3 artifacts/css-style-query-handoff-model-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-style-query-handoff-model-20261110-v1/review-replay
```

The output directory must not exist. Receipts retain exact source hashes, axiom
inventories, observations, and mutation diagnostics. Browser evidence and the
known-bug assessment belong to the separate parent investigation; this model
adds no browser finding or repair count.
