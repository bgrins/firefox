# Completed task Cargo-target inventory

Read-only inventory; nothing deleted. Four generated Cargo target directories from my completed Ahom validation/replay total **1,228,864 KiB (1.172 GiB)** according to `du -sk`. All four are outside their enclosing frozen source manifests. Exact absolute paths and sizes are in `TARGETS.json`; manifest/receipt associations are in `ADMISSION.json`.

Common prefix: `/Users/bgrins/code/firefox/artifacts/css-line-break-language-proof-v1/`.

| Relative target | KiB | Ownership and evidence |
|---|---:|---|
| `research/ahom-candidate-native-v1/build/icu` | 306616 | My completed candidate replay. Generated RESULT equals retained evidence RESULT byte-for-byte. Manifest336dffbe excludes target; run-candidate.py regenerates it with Cargo offline. |
| `research/ahom-candidate-native-v1/imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/development-build/icu` | 307676 | My copied baseline provider replay; imported dictionary-stream source manifest4987e143 excludes target. Its source-only check regenerates baseline ICU. |
| `development-build/ahom-candidate-relocated-v1/build/icu` | 306712 | My completed relocated candidate replay; same source seal and byte-identical retained RESULT. |
| `development-build/ahom-candidate-relocated-v1/imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/development-build/icu` | 307860 | Baseline provider output inside that completed relocated copy; same imported dictionary-stream seal. |

These exact four targets are eligible for deletion **after root confirms no active replay is using them**. I have no active compiler or replay against these paths. The attempted process snapshot (`ps -axo pid=,command=`) was denied by the sandbox, so I cannot attest that another worker/root has no open consumer. `PROCESS-CHECK.json` records this limitation; no escalation or permission request was made.

Only the listed `icu` target directories are proposed. Preserve enclosing source capsules, manifests, source inputs, tools, retained evidence, raw logs, build RESULT/COMMANDS receipts, and Cargo source/vendor caches. Replaying after deletion rebuilds targets; it does not require regenerating evidence from memory or a network fetch. Do not remove an entire import or research capsule just because it contains one generated directory.

The bounded scan also inspected historical task-named roots immediately under `/private/tmp` containing numeric, sigma, timeline, rlh or coordinate names. It found no additional Cargo targets identified by `.rustc_info.json` plus a debug/release directory in the searched non-source/vendor trees. Several historical temporary roots contain generated C++/Lean outputs, logs and copied sources; these are not proposed for deletion without their own receipt/reference audit. This inventory is not an exhaustive filesystem cleanup.

Explicit exclusions: root `objdir-full.noindex`; current parser producer/reviewer directories including `css-parser-public-history-admission-development-v1/relocated/output`; other workers' outputs; user-home caches. None was searched for deletion or changed. No live source, WPT, Git/index/ref, browser or native build action was performed.
