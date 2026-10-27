# Calculated jump-none minimum: root acceptance record

Proposed fix 133, tentative P3 conformance. Calculated counts such as calc(1), calc(0), negative values and NaN now reach the jump-none minimum of two at computation. Invalid literals and unresolved contextual calculations retain rejection. The exact patch contains one Rust file and three WPT files.

| Phase | PASS | FAIL |
|---|---:|---:|
| Original | 52 | 25 |
| Candidate | 72 | 5 |
| Restored | 52 | 25 |

All 22 focused cases pass, repairing 20 observed failures. All 55 controls and all 77 restored observations match exactly; each phase completes four OK harnesses. Candidate and restored builds pass. The original cleanup-only wrapper failure remains retained, with separate process/state reconciliation before continuation. Final native and WPT sources are restored. Raw index bytes changed with unknown cause; semantic staging and original working differences are preserved.

The current HEAD four-path patch roundtrip passed. No clean-HEAD browser build is claimed. Scoped WPT lint and Rust formatting evidence are retained. The five unrelated failures, contextual easing work in bug 2037743, performance and security impact remain outside the claim.

Discovery came from source/specification audit and browser reproduction. Lean separately checks conditional origin-sensitive consumer laws, reusing canonical numeric proofs; it does not prove native parsing, IEEE behavior, context resolution or complete CSS semantics. No proof-discovery or canonical coverage credit is added.

This is a root-reviewable acceptance record, not a staging, installation or signing action. Existing ROOT-OUTCOMES, STANDALONE and PENDING records remain unchanged. Root owns final adoption, counts, ledgers and the separate research then four-path native/WPT commits.
