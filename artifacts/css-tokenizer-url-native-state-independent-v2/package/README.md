# URL native state and raw source capture

Source-only companion to the accepted URL provider model. Authenticate `FREEZE.json`, `MANIFEST.json` and `check.py` against the separately communicated hashes before execution.

```sh
python3 -I -S /absolute/path/css-tokenizer-url-native-state-v2/check.py --run --output /absolute/new/output-directory
```

The output must be new and outside the input capsule. The checker authenticates the exact closed roster before creating it, regenerates complete source bindings, freshly compiles Lean, audits every theorem, runs semantic mutants, builds the actual native crate and compares state/capture traces. Dependencies are included except the explicitly pinned installed toolchain. No Firefox build or browser is run.

Read `REPORT.md` and `SOURCE-ADMISSION.md` for claims and premises. This is a formal model and bounded source correspondence component, not a whole-tokenizer, compiler or memory-safety proof. The accepted provider predecessor and rejected v1 validator capsule are unchanged. V1-TRANSFER.json authenticates all unchanged inputs; validator-history retains the failure evidence.
