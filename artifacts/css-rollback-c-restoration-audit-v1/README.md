# Paired C restoration audit

Prepared only; execution requires the parent to confirm the corresponding owner terminal. This independently checks restored source bytes and identities, preserved ArcSlice/context sources, HEAD/index/staged/unrelated diffs, bundle/extra semantics, backup/lock removal and fresh process-group absence. Results describe restoration and browser observations, not native fix acceptance.

Run with isolated Python and explicit `--runtime`, `--config`, `--result` (new filename inside this directory), `--owner-launch`, `--owner-session`, `--owner-terminal`, and `--owner-exit`. Baseline uses css-rollback-c-baseline-runtime-v1 and css-rollback-c-baseline-native-v1/CONFIG.json; candidate uses their candidate equivalents. Keep BASELINE.json and CANDIDATE.json separate. The audit reads exactly the config hash/runner hash captured in each runtime BEFORE.json and the pinned bundle helper. Process records must include build, wake, primary and control groups; missing records fail instead of implying cleanup.

Syntax checked with ast.parse. No live audit was executed during preparation. Fresh ps may require sandbox elevation. No source/index/native build/browser mutation is performed by this audit.
