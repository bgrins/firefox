# MinMax publication execution template

The driver is byte-identical to native-publication-v2/run.py and POLICY.json to disabled v1. No current HEAD, research receipt, controls, source identity or successful signature is prefilled. The wrapper creates exclusive two-payload install/commit owners; it never rewrites this template. Only root executes the three commands after independent native-trial restoration and the actual signed research checkpoint.

From the repository root, replace uppercase arguments with actual values:

```
python3 -I -S -B artifacts/css-minmax-native-publication-v3/publish.py install --manifest TEMPLATE_SHA256 --receipt ACTUAL_RESEARCH_RESULT --receipt-sha256 ACTUAL_RESULT_SHA256 --branch ACTUAL_REFS_HEADS_BRANCH
python3 -I -S -B artifacts/css-minmax-native-publication-v3/publish.py delivery --manifest TEMPLATE_SHA256
python3 -I -S -B artifacts/css-minmax-native-publication-v3/publish.py commit --manifest TEMPLATE_SHA256
```

Install authenticates the template and frozen inputs, invokes the existing read-only extractor, verifies the actual research commit signature, and creates artifacts/css-minmax-native-publication-install-v3. Its policy enables only install, binds the emitted current-state values, and pins every template payload and its invocation manifest without a self-reference. The unchanged driver performs full current/source/index/ownership/quiescence checks and writes its normal INSTALL-RESULT. The signed research HEAD must still be current; do not insert an artifact commit before MinMax.

Delivery authenticates the actual installed owner using INSTALL-RESULT.manifest_sha256 and reconstructs its exact policy. It executes POLICY.lint_command verbatim, retaining command, full output and exit. A nonzero exit prevents the delivery receipt. Lint's successful exit is the zero-error contract; no success is inferred from a pre-install lint. It imports the genuine WPT Manifest API and updates only the two installed paths, verifying exact testharness filenames, default URLs and Git-blob SHA1 values against unchanged SHA256-pinned bodies. The subset manifest is saved under the owned publication runtime, never in the canonical manifest. COMMANDS records the actual invoked Python argv separately from the Manifest API description. All evidence hashes and the installation manifest enter DELIVERY.json. No browser or build runs.

Commit reconstructs the same installed policy, requires current epoch bytes to match the actual installation receipt, binds the actual three controls and hashed delivery receipt, and creates artifacts/css-minmax-native-publication-commit-v3. The accepted-claims calc preimage remains b291; the unchanged commit driver checks current065c separately. It requires commit.gpgsign=true, signs exactly calc plus the two MinMax WPTs through its temporary index, validates parent/tree/signature and synchronizes the canonical epoch. Existing failure journals, lock behavior and no-automatic-retry policy remain unchanged. The wrapper propagates the driver's exit. Neither publication nor delivery claims an app rebuild, ledger acceptance or accepted-count increment.

Output directories are exclusive. A failed installation, lint, manifest, signing or wrapper step retains its evidence; a retry requires a separately reviewed output decision. No wrapper tries to repair a failed publication. A failure before driver startup can leave only a bound owner directory; it has not installed native files.

check.py authenticates the seven frozen references and exact driver/policy, then uses owned removed scratch with a fake lint process and fake Manifest class. It tests bound-owner authenticity/exclusive creation, successful delivery receipt, wrong blobs/URLs/extra entries, duplicate delivery and failing lint. These mocks do not establish actual installed lint, Manifest imports or native signing. Existing extraction/signing/source guards remain the executed driver's responsibility. The first mock attempt b229df failed because the fake subprocess lacked STDOUT; adding that fake constant yielded cc18c8/0 without production changes. The concrete template awaits actual root execution.
