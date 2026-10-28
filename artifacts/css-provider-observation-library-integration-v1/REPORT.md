# Additive ProviderObservation integration

Added `artifacts/css-spec-lean/CssSemantics/ProviderObservation.lean` with exactly the independently reviewed source bytes: SHA256 dae3b26de60f862ce9c21b25144d451748c23f927613f7e5febf1b30f302f8d5. No source changes to the generic proof were needed. Its only direct import is the existing TransitionMachine; no Gecko adapter enters the core.

A relocated replay containing only these two library modules and the dedicated entrypoint passed. It compiled the library imports and audited every local theorem, with only propext/Quot.sound. This demonstrates path independence on the current host, not testing of another compiler platform. Both the replay's temporary compiler directory and the outer relocation directory were removed. Exact command, source identities and preservation check are in INTEGRATION.json; raw compiler/audit outputs are in portable-replay/.

All 2,002 pre-existing core modules and root-level library files in BEFORE-LIBRARY.json rehashed unchanged. The sole addition in that scope is ProviderObservation.lean. Existing central aggregator, check.py, coverage inventory, toolchain and package files were left untouched. No native source, browser, Firefox build, index or commit operation occurred.

Run again from the checkout with a fresh output directory:

```sh
python3 -I -S artifacts/css-provider-observation-library-integration-v1/replay.py \
  --manifest-sha 9931ccf125796bb5ace745af8e3cda23f4b6265bd82eebfa30acf97c29fa76ba \
  --library artifacts/css-spec-lean \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --lean-sha d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf \
  --output /absolute/fresh/output
```

Consumers may use `import CssSemantics.ProviderObservation` directly. Remaining integration work is deliberate central aggregator/audit inventory registration with updated pins, and any downstream specification/native observation adapters. SCOPE.md maps this addition to infrastructure only: no new CSS specification coverage, full CSSOM geometry or native provider-correctness claim. EVIDENCE-LINKAGE.json retains the external MathML example and both rejected erroneous adapters; the portable import replay does not rerun or count those historical validations.
