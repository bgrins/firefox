# HEAD-only port

Exact historical base c1f4ca1d36002ed3f9551facf14cbaf718828c61 was read with git show (parent explicitly requested these read-only commands). No Git/index/worktree mutation was performed.

`original/` contains both complete HEAD files. `candidate/` contains only the namespace-key repair. `native-head.patch` is regenerated from those complete files; hashes in PINS.json. This is an artifact-only port, not a separately compiled/tested build.

Difference from local tested candidate: HEAD's cascade.rs imports only FxHashMap near its header, while the local experimental file had moved that import and added FxHashSet. The port changes the existing HEAD import to `{FxHashMap, Namespace}` without adding FxHashSet. All other native key patch hunks applied unchanged with line offsets. The first artifact patch attempt's import-context rejection is retained in apply.log and initial-apply-diagnostics; that one import was then adapted exactly. Full local experimental DeclarationIterator/source-block/revert-state changes were NOT transplanted. The custom_properties.rs candidate is byte-identical to native candidate v2 because its HEAD original matches the frozen baseline.

The checker regenerates the exact standalone diff and verifies that removing the namespace repair from each original/candidate comparison leaves no unrelated additions. Root should independently apply/reverse this patch at the pinned commit and review final formatting. The existing combined-tree runtime gate is not an isolated-HEAD build claim.
