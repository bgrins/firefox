# Protected Lean comparison pilot

The installed checkers can replay a real CSS numeric-model theorem from a locally generated export. The installed Lake comparison and axiom functions distinguish a correct proof from a changed transitive definition, an added premise, and an unapproved axiom. These local runs are diagnostics on reviewed, self-authored fixtures. **Official isolated `lake comparator` and `lake check` acceptance remains pending on Linux.** Both commands refuse this macOS host with exit 2, even with supplied exports. No sandbox bypass was used.

## Selected contract

`NumericDigits.scan_reference` states, for every finite list of bytes (`Fin 256`), that the scanner's digits and remainder equal the independent `takeWhile`/`dropWhile` reference. `digit` checks the inclusive ASCII range 48–57; `referenceDigit` tests membership in `"0123456789"`. There is no caller premise to make vacuous. `Audit.lean` supplies the concrete input `[48,57,65]`, consumed prefix `[48,57]`, and remainder `[65]`.

This is a correspondence between two Lean models. It does not verify compiled Rust, floating-point conversion, CSS source interpretation, the surrounding tokenizer or all CSS. Arbitrary bytes are intentional here; the larger numeric-entry model's normalized-ASCII caller restriction is not needed by this digit-scan lemma.

The complete original module is preserved. The challenge is an exact source prefix through `scan_reference`, followed only by the closing namespace. All project definitions on the theorem's transitive dependency path are included; later unrelated theorems are omitted. Imported standard-library proof dependencies are retained in the complete, compressed challenge export, with its root list, raw-byte hash and declaration count. This is not merely a copy of the theorem's visible text.

The local canonical integration was applied but not committed when this capsule was prepared. Its exact source bytes were independently authenticated against Firefox research commit `5a9dc434eff56b9f65b27f1d2ae8ce35251b38f2`, path `artifacts/css-tokenizer-numeric-admission-v1/lean/NumericDigits.lean`. `PINS.json` identifies that source, the preceding canonical HEAD, nine tool binaries, selected installed checker/module libraries and preserved implementation sources. Toolchain binaries and their corresponding distributed sources are trusted inputs; this experiment does not prove their compilation correspondence or pin the entire host OS.

## Four fixtures

| Fixture | Change | Installed comparison diagnostic | Installed axiom diagnostic | Direct kernel observations |
| --- | --- | --- | --- | --- |
| good | Original exact theorem and proof | Match | Permitted | All six bundled checkers accept |
| changed-predicate | Digit upper bound becomes 56 and reference string loses `9`; theorem remains valid for the altered language | Rejects transitive `NumericDigits.referenceDigit` identity | Permitted | Ordinary Lean and Nanoda accept this different valid specification |
| extra-premise | Adds `impossible : False`; proof is `False.elim impossible` | Rejects theorem statement | Permitted | Ordinary Lean and Nanoda accept the vacuous statement |
| forbidden-axiom | Exact original statement, proof calls `NumericDigits.forbidden` | Match | Rejects forbidden axiom | Ordinary Lean accepts the declared axiom; configured Nanoda refuses it |

Nanoda's observed refusal is exit 101 with an unknown-declaration panic for the skipped, unpermitted axiom. It is recorded as that diagnostic refusal, not as a polished Lake verdict. Plain `leanchecker` checks well-typedness in the supplied environment and does not by itself impose our axiom whitelist or protect the intended theorem statement.

`Diagnostic.lean` is only an adapter calling the installed `Lake.Check.compareAt` and `Lake.Check.checkAxioms`. It implements neither algorithm. Its primitive root list is checked against the preserved installed `primitiveTargets` source. Like Lake, it provides no definition holes and explicitly permits only `propext`, `Quot.sound` and `Classical.choice`. It prints both classifications and exits zero even on mismatch; `run-local.py` checks each exact expected classification. A diagnostic process exiting zero is not an acceptance verdict.

The comparison is intentionally conservative constant identity, including transitive definitions; it is not a proof that arbitrary rewritten definitions are semantically equivalent. The target proof may vary while its statement and protected dependency meanings remain fixed.

## Local reproduction

```
python3 -I -B replay.py --toolchain /path/to/pinned/darwin-toolchain --out /new/output
```

The source-only allowlist is sufficient with the pinned installed toolchain; no canonical checkout, network, browser or old build is used. Each run builds the small source fixtures in a fresh temporary directory, exports explicit roots with the installed exporter, invokes the installed comparison functions, and checks actual exports directly with the six bundled checkers. It also materializes the dependency-free Lake manifest with a local build of the reviewed TOML project. Temporary compiled output is removed. The challenge export is retained compressed; variant exports are reproducible and their exact hashes and root lists are retained. Command outputs and classifications are recorded individually.

Only the good fixture is replayed by all six checkers; the three adversarial fixtures are replayed by ordinary Lean and whitelist-configured Nanoda. The comparison and axiom diagnostics run for all four. This scope is deliberate.

## Linux acceptance recipe (not executed here)

Provision the matching Lean release and working bubblewrap on a separate Linux environment. Independently approve the Linux binaries; the Darwin binary hashes cannot authenticate them. Put this source package, configuration, approved challenge and toolchain under reviewer ownership, outside the proof worker's write permissions. Hashes alone do not establish that access boundary. Only the submitted solution and disposable build area should be worker-controlled.

```
python3 -I -B run-linux.py --toolchain /reviewer/lean-4.35.0-rc4 --out /new/linux-results
```

This prepared, unexecuted runner invokes the **official** `lake comparator --paranoid` on all four projects. It never uses `--inadvisably-no-sandbox`, refuses non-Linux hosts, and removes the internal `LAKE_CHECK_EXPORT` environment switch. The installed comparator itself performs sandboxed project evaluation/build/export and comparison; there is no custom substitute acceptance gate. The expected result is one accepted solution and three specific refusals. The dependency-free manifest is included so the sandbox need not write it into its read-only project.

An optional approved, uncompressed export can also be checked with the official command:

```
python3 -I -B run-linux.py --toolchain /reviewer/lean-4.35.0-rc4 --out /new/linux-results \
  --check-export /reviewer/challenge.ndjson --check-export-sha256 REVIEWED_HASH
```

That adds `lake check --paranoid --from-export`. Its result concerns that exact export, not correspondence to an arbitrary project directory. Full-project `lake check` exports everything in scope, including the imported standard library; this pilot does not promise or run that much broader check. Linux namespace availability, mounts, resource limits, actual reviewer/worker ownership separation and the prepared runner remain unvalidated here. No host installation, VM or GCP change was made.

## Source inspection

The retained `Lake/CLI/Check.lean` shows the non-Linux refusal in `mkContext` before the supplied-export path is used. `compareAt` checks theorem statements and walks protected transitive constants; `checkAxioms` walks proof dependencies. `LeanChecker.checkExport` replays the exported environment but has no whitelist. `Lake/CLI/Main.lean` explains the broader full-project export path. The exporter has no ordinary help handler; its actual argument partitioning is retained in `LeanExport.lean`. Only `lake help comparator` and `lake help check` are treated as authoritative command help.

This prototype narrows the practical next step to a protected Linux run of this fixed matrix. It does not establish correspondence between CSS prose and the chosen Lean definitions.

`check-linux-orchestration.py` is a Python-only control for the optional export argument/receipt path. It intercepts every subprocess and uses mock responses; its result is explicitly not Linux or comparator acceptance. The separate actual platform-refusal observation runs the unmodified launcher on Darwin and confirms no output/build directory is created.
