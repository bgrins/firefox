# Completed diagnostic pilot

The final cold source-only replay passed against 28 authenticated source inputs. It retained 34 command receipts, four compiled fixture exports, exact diagnostic classifications for all four fixtures, and direct acceptance of the good export by all six bundled checkers. The challenge export contains 3,546 transitive declarations and is retained compressed; its raw hash matches the exporter receipt. All command outputs retained as logs or export hashes were reauthenticated.

The unchanged installed comparison algorithm rejected the modified transitive reference predicate and the added False premise. Its separate axiom traversal rejected the unapproved axiom. Ordinary Lean replay accepted all four well-typed exports, while whitelist-configured Nanoda accepted the first three and refused the forbidden-axiom export with its observed exit-101 unknown-declaration panic. These are different checks, not contradictory results.

Both official Lake commands returned exit 2 on Darwin, explicitly requiring Linux namespaces even with supplied exports. No sandbox-disabling flag was invoked. The Linux recipe remains unexecuted. A separate Python-only mocked orchestration check exercises its optional approved-export receipt path; all five subprocess calls were intercepted and no native commands were executed by that control. A real Darwin launcher refusal also confirmed no build/output directory was created.

The frozen source manifest is `825aa0cde3ca61cd016de90cffcd4412638a13369fcc034a407adbbafa8240c6`. The final receipt is `source-only/REPLAY.json`; detailed observations are `source-only/diagnostic/REPORT.json`. The preceding successful author diagnostic is preserved in `diagnostic-3`, with an identical semantic report.

All owned temporary source/build directories were removed; no .olean, .ir, .lake or Python cache remains in this capsule. The artifact is approximately 5.8 MB, chiefly two compressed copies of the checked transitive challenge export. No canonical source, native code, browser, Git/index, host installation or VM configuration was changed.

The next necessary environment is Linux with working bubblewrap and separately protected reviewer inputs/toolchain. Only an actual official run there can establish the promised isolated acceptance. This capsule provides reproducible diagnostics and a reviewed-source recipe, not that result, and not native Rust or CSS-prose refinement.
