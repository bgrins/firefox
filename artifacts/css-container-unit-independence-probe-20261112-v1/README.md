# Container units in registered initial values

This capsule reproduces one pre-existing CSS conformance defect: container-relative lengths are accepted in registered initial values that must be computationally independent. Source/spec trace is retained separately in `../css-native-length-entry-target-20261112-v1/CONTAINER-TRACE.md`; the target capsule is still a draft, not a proof artifact.

The existing upstream WPT ran against the parent-pinned local binary and produced its six expected failures. Only the first test directly exposed missing rejection; because every test reused --x, the remaining five failed with InvalidModificationError after the first registration succeeded. `BASELINE-OBSERVATIONS.json` preserves that distinction.

The separate unique-name diagnostic covers all six units, both JavaScript registration and @property, both length and length-percentage syntax, and direct/calc/additive-calc forms. All 72 rejection cases fail on the baseline. All 18 ordinary container-length controls and 16 absolute/viewport-positive/font-negative registration controls pass. `CONTROL-OBSERVATIONS.json` records the full matrix, backed by the raw WPT report/log and pinned binary hashes.

`candidate.patch` contains a proposed shared container-unit admission guard, an expansion of the existing WPT, and removal of its six expected-FAIL entries. All six original test names are preserved; the existing conditional x86 crash expectation is preserved because this host run does not resolve it. The final candidate test itself was run on the unchanged baseline binary: the same 72 FAIL and 34 PASS results, with testharness status OK and expected process exit 1. `CANDIDATE-BASELINE-OBSERVATIONS.json` links each result to its independently declared case.

The initial sandboxed harness attempt failed before browser launch on the .mozbuild lock. It is retained. The subsequent local WPT invocations were automatically approved and used the existing build; no native build was run by this agent. Each temporary owned probe was removed in finally. Original native/WPT/metadata files were not modified by this agent. The three candidate payloads and original hashes were handed to the parent for live installation and native validation; no post-fix result is claimed in this capsule.

This defect was found through source/spec correspondence investigation and browser tests, not proved or discovered by a completed new Lean or Kani theorem. The broader standalone grammar proof and its canonical transport remain separately accepted and frozen.
