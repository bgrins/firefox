# Animation-taint substitution model

This small Lean model verifies the destination guard and fallback selection with
animation taint supplied as input. It provides a contract for a native repair,
not a complete animation-taint acquisition policy or a proof of Stylo.

`Model.lean` contains an executable evaluator and a separately stated inductive
relation. A binding has an already-computed optional payload and an independent
animation-taint bit. The payload carries opaque tokens and attribute metadata.
References in selected fallbacks use the same destination classification.

The 21 checked laws establish:

* Bidirectional correspondence between evaluation and the declarative relation,
  and uniqueness of the result.
* Rejection before fallback selection for an animation-tainted source in a
  nonanimatable destination; preservation in an animatable destination.
* No lookup of an unused fallback, recursive handling of a selected fallback,
  and propagation of a selected fallback's failure.
* Preservation of attribute metadata, which does not itself trigger this gate.
  Equal tokens with different animation taint can produce different results.
* Least infectious closure for externally supplied seeds and reference edges,
  monotonicity under larger inputs, and a conditional bridge to substitution
  when an environment's taint bits satisfy seed and dependency obligations.

The model deliberately does not identify reference edges with its evaluation
trace. The current infectious-property prose does not explicitly exempt unused
fallback references. Consequently, skipping an unused fallback does not prove
that a containing custom property is untainted. Acquisition, inheritance,
registration, inactive keyframes, transitions, and WAAPI policy remain outside
the theorem. `MAPPING.md` states the full abstraction boundary.

## Validation

Lean 4.35.0-rc4 accepted all 21 laws. Their axiom audit contains only Lean's
standard `propext` and `Quot.sound`; the four core graph-closure laws need neither.
There are no admitted proofs or added axioms. Fourteen executable observations
cover blocked/allowed destinations, empty versus absent fallback, nested
fallbacks, both independent taint bits, and equal-token provenance changes.

Six type-correct mutations are each rejected by the unchanged laws and an exact
false semantic witness: omitted gate, overbroad gate, conflated attribute gate,
eager unused fallback, lost attribute payload, and discarded fallback. A seventh
control rejects a changed specification snapshot. An arbitrary compile error
does not satisfy the semantic-witness check.

The full primary Variables Level 1 snapshot is pinned by SHA-256; three exact
HTML excerpts map the replacement algorithm, infectious paragraph, and unresolved
acquisition boundary. Source-only replay copies exactly eleven input files and
builds them in a fresh temporary directory. All owned compiled output is removed.
No live Firefox code, WPT, canonical CSS library, browser, or Git state is changed.

From the Firefox repository root:

```sh
python3 artifacts/css-animation-taint-substitution-model-20261110-v1/replay.py \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --out artifacts/css-animation-taint-substitution-model-20261110-v1/review-replay
```

The output directory must not already exist. `source-only-replay/report.json`
records the completed independent-directory replay; its verification receipt
contains every input hash, theorem audit, observation, and control.

## Native integration obligations

The native producer must supply a justified taint policy, preserve provenance
through aliases and typed/token conversions, keep it significant in map/cache
deduplication, and pass correct animatability for longhands and shorthands.
Rejecting one substitution must not destroy the custom property's stored value.
None of these implementation obligations is established by this model. Generic
animation-value conversion also serves CSSOM and transitions; marking every
conversion is not justified by the destination theorem.

The local and installed-browser failures are recorded separately in
`../css-animation-taint-calibration-runtime-20261110-v1`. This artifact adds no
repair, browser observation, novelty claim, security claim, or termination result.
