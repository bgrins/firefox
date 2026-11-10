# Standalone streaming proof integration candidate

`library.patch` integrates the root-replayed finite DOMString streaming proof
into standalone library base `0127c4f42c620cdaba4f9b92cca93ca95df2d913`. Final patch SHA-256:
`130885648c9163f7b9fba02e1cf65701e98b4cb1da49ad0f117dbae448dbe7c7`. The canonical library, its Git index, and its preexisting
untracked `.DS_Store` were not modified.

The 15-file candidate adds seven modules under `CssSemantics.Streaming` and
`CssSemantics.StreamingExamples`, plus standard imports, theorem audits,
executable registration and coverage/source-contract documentation. Twenty-seven
proofs transfer with namespace/import changes; an aggregate kernel-checked
example theorem is added. Thirty-two labels receive a `streaming ` prefix.
Existing input definitions are unchanged. The generic machine, adapters and
pipeline preserve both carries and ordered EOF flushing.

Validation passed from a fresh Git archive with no preexisting Lean objects:
17 affected modules, 98 audited declarations (28 new), and 111 observations
(32 new plus 79 existing scalar/codepoint/DOMString controls). Only the standard
`propext`, `Quot.sound`, and `Classical.choice` axioms occur. Two deliberate
registration corruptions were rejected and restored. Global static coverage
checks 11,923 exact audit registrations. This is not a full-library or browser
gate refresh. The original artifact's six semantic mutants and three origin
drift controls remain historical evidence; they were not rerun here.

`verification2/REPORT.json` is the clean Lean receipt. A final formatting-only
adjustment preserved existing Unicode spelling in coverage.json; its parsed JSON
value is unchanged. `FINAL.json` binds that receipt to the final patch, verifies
all compiled module hashes unchanged, and records the repeated static coverage
check. `verification1` records an earlier wrapper failure: its expected vector
included unrelated input-trace examples; all compiled proofs passed. The selector
was corrected before the clean successful run. All scratch libraries and Lean
objects were removed.

`ORIGIN.json` authenticates the seven source modules and two input manifests
against Firefox commit `d34a26d38d78`. `SOURCES.json` records the mapping and exact
base/candidate hashes. `CONTRACT.md` is the source of the candidate's terse
`research/domstring-streaming.md`; its explicit domain and exclusions are kept.

Reproduce from the Firefox checkout, with an unused output directory:

```sh
python3 artifacts/css-domstring-streaming-library-20261110-v1/check.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-domstring-streaming-library-20261110-v1/review-replay
```

The checker applies the patch only in a temporary Git archive. Root owns review,
application to the standalone library, and signing. The model proves finite
semantic refinement of a manually reviewed source contract; it does not prove
prose translation, CSSOM coercion, byte decoding, Firefox/native correctness,
infinite-stream productivity, allocation, stack, or performance properties.
