# Next completed-target cleanup batch

Read-only inventory; no deletion or build. Propose **six exact Cargo target directories, 701,792 KiB (685.344 MiB)**. `PROPOSED.json` contains absolute paths, byte-pinned completed replay receipts, authenticated source closures and exact source-only regeneration commands. Root must perform its own current ps/lsof no-use gate before deletion.

All source files in the six associated capsule checks were rehashed successfully:16,732 input checks including the same7,495-file Ahom closure checked for both targets. No proposed target is a source input. The prior four targets deleted under root's cleanup receipt are absent and not proposed again.

Paths below are relative to `/Users/bgrins/code/firefox/artifacts/`:

| Exact target directory | KiB | Completed receipt / ownership |
|---|---:|---|
| `css-ahom-lf-partition-probe-v1/root-full-replay-v2/imports/lf-complex-stream-diagnostic-v1/imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/development-build/icu` | 307532 | Root historical Ahom replay; `css-ahom-lf-partition-probe-v1/ROOT-FULL-REPLAY-v2.json`, exit0 and7,495 authenticated inputs. |
| `css-ahom-lf-partition-probe-v1/root-full-replay-v2/build/icu` | 306392 | Same completed root receipt. |
| `css-tokenizer-url-native-state-v2-replay-v1/output/native/fast-release/macro-build/target` | 21972 | `output/REPLAY.json`: PASS,442 inputs,51 modules388 audits. Historical component replay. |
| `css-tokenizer-url-native-state-replay-v2/output/native/fast-release/macro-build/target` | 21968 | `output/REPLAY.json`: PASS,428 inputs,51 modules388 audits. Historical component replay. |
| `css-tokenizer-url-provider-replay-v2/result/native/fast-release/macro-build/target` | 21964 | `result/REPLAY.json`: PASS,436 inputs,34 modules281 audits. Historical component replay. |
| `css-tokenizer-url-provider-replay-v1/result/native/fast-release/macro-build/target` | 21964 | `result/REPLAY.json`: PASS,436 inputs,34 modules281 audits. Historical component replay. |

The Ahom checker regenerates baseline and candidate ICU from pinned vendored source with offline Cargo. For URL packages, `source/native/build.py` creates the macro-build project and executes Cargo with `--offline --locked --target-dir`; `source/check.py --run --output NEW_EXTERNAL_OUTPUT` reproduces the full source-only replay. Commands are recorded per target in the JSON. Use a fresh output for those URL checkers; they reject reusing an existing output root. No vendor, toolchain, macro source or source capsule is proposed for deletion.

Keep the surrounding completed output trees' logs, REPLAY/RESULT JSON, commands, source-binding records, generated source witnesses and integrity receipts. The proposal is only the six terminal Cargo directories, not their enclosing build, output, imports or source directories.

The URL outputs are associated with completed receipts, but this agent is not claiming exclusive current ownership. A direct query to the former producer's canonical agent path returned no live agent. Root's active-use confirmation remains necessary; no inference from absent agent alone authorizes deleting something in use.

## Bounded search and exclusions

The scan was restricted to `artifacts/css-*` directories, pruned source/sources/vendor/toolchain trees and Cargo debug/release contents, and excluded `css-parser-*`, cleanup and inventory directories. Cargo targets were recognized by `.rustc_info.json` plus a debug or release directory. `CANDIDATES.json` retains the full small discovered list; entries not in `PROPOSED.json` are **not** recommended for deletion because their development-task ownership/completion was not adjudicated.

This method deliberately misses some outputs beneath pruned source paths and non-Cargo generated trees; it is not a full repository/home inventory. It does not inspect or propose root's `objdir-full.noindex`, the active parser producer/reviewer outputs, or user-home caches. No native source, WPT, Git/index/ref, browser or production build action occurred.
