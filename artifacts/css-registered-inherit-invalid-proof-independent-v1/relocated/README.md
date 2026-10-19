# Registered explicit-inherit component

Run from any working directory:

```sh
python3 -I -S /absolute/path/to/css-registered-inherit-invalid-proof-v1/check.py --output /private/tmp/new-inherit-proof-replay
```

Requires Python3, /usr/bin/patch and Lean 4.35.0-rc4 at the path/hash in TOOLCHAIN.json. The matching standard Lean installation (implicit Init environment) is a trusted external toolchain dependency. No network, Git, Mach, Rust build or browser runs. An output directory must not already exist.

The checker authenticates every input before loading helpers, reextracts all twelve full source records, compiles the model, audits the exact seventeen theorem names, checks four compiled semantic mutants and verifies exact native artifact patch application/reversal. Generated outputs stay in the requested external directory. SCOPE.md and SOURCE-MAPPING.md preserve the conditional native admissions; runtime-context is root evidence rather than a proof premise.
