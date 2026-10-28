# Disabled four-source grid rollback typecheck

This preparation targets exactly the four sources from css-random-typed-parse-rollback-proposal-v4, including the corrected PropertyDeclarationContext receiver in shorthands.rs. It excludes the independent line-height font.rs change. The reviewed run.py, staged-aware epoch/projection helpers and synthetic checker are byte-identical to css-random-line-height-typecheck-v2; only the package, source roles, scope and absent output directory are rebound.

Execution is disabled. Root must first verify that the ongoing paired line-height browser experiment has terminated and restored original source/application state, then review an explicitly enabled successor in an exclusive execution window. No compiler or live guard is run by this preparation. The existing source-transition lock remains a hard exclusion. Historical runtime/HEAD and staged165 bindings are retained, not silently projected onto a new signing state.

The inherited mechanism temporarily installs four authenticated in-place sources, uses the configured Firefox Rust graph with two jobs/offline Cargo check and existing objdir, then restores exact source bodies after all compiler groups terminate. Root/nested semantic indices, full staged165 patch/blobs/modes, index flags, installed WPT identities, binary pins and runtime control bytes must remain unchanged. Raw index-stat observations may differ but no runtime epoch or signing state is published. No browser linking, native acceptance or new target directory is requested.

The configured check is the missing validation for v3's caught method-receiver defect and v4's correction. Formatting and patch transport are not native typechecking. The existing WPT v3 remains unchanged at26 ordinary assertions; this package executes no WPT.

A future enabled successor would use the inherited command interface and absent output artifacts/css-random-grid-typecheck-runtime-1. Do not execute this disabled package or alter its seal to bypass the activation boundary.
