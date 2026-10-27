# Whole-provider rectangle observation capsule

`lean/CssSemantics/ProviderObservation.lean` is a reusable generic module over the existing TransitionMachine runner. Query success identifies both the provider-returned world and an observation resolved in that world. Observation erasure commutes with queries and histories while preserving the complete world and success/failure. `lean/MathMLRectObservation.lean` specializes this to c3's equal-size, different-position observations and derives admission from the existing Subtree marking proof.

Run with the recorded SHA256 of `FILES.json` and a fresh output directory outside this capsule:

```sh
python3 -I -S replay.py --manifest-sha SHA256 --repo /Users/bgrins/code/firefox --output /absolute/fresh/output
```

The replay authenticates the closed capsule roster, pinned existing imports, compiler, and retained measurement bindings. It compiles the modules, checks every local theorem's axioms, and requires both erroneous adapters to be rejected as false by kernel `decide`. Temporary compiler products are removed on success or failure. No native build or browser command runs; existing library modules are copied unchanged into a temporary directory.

The two negative controls isolate selected-size-only publication and observation before forcing. Both retain a correct completion/eligibility transition. Deleting the target after forcing yields no successful observation. This is Option failure, not rollback or a CSSOM empty result. See SCOPE.md for lifetime, horizontal-writing-mode and native-correspondence limits.

The trace observations are retained empirical evidence, not kernel proofs about Gecko. The whole-provider coordinate update is stipulated in the example. These results extend the previous Size-only observation model without claiming complete CSSOM geometry or native repair correctness.
