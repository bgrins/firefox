# Until-after native/model calibration

**PASS within the stated finite projection.** The capsule remains unsealed for root source/proof review. `UntilAfter.lean` was not changed.

The final fresh replay (`final-v2/RESULT.json`) compiles 56 reachable Lean modules, then compares **27 histories / 138 snapshots** against the complete retained cssparser implementation in debug and release. Both agree byte for byte. The driver exposes requested punctuation, outer ownership including overlaps/closers, pending function Stop/Consume behavior, cached delimiter read/reset/re-read, matching/mismatched/unterminated curly recovery, URL directive writes and var/env/attr observations. Nonzero depth/limit values are preserved. No Firefox/browser build occurred.

Six mutants compile and execute successfully with the same 138 snapshot identities and arities. Differences are semantic state observations, not compiler or debug-assertion failures:

| Mutant | Changed rows | First distinguishing effect |
|---|---:|---|
| Outer ownership ignored | 25 | Outer-owned semicolon advances from byte4 to5. |
| Missing direct advance | 41 | Requested semicolon remains at byte0 instead of1. |
| Omitted curly cleanup | 22 | Position remains1 instead of23; var observation is missed. |
| Ignored Stop/error guard | 7 | Failed pending-function state advances despite Stop. |
| Cache overwrite | 11 | Previously retained function cache is cleared. |
| Erased curly writes | 5 | Final sourceURL B.css and sourceMappingURL M.map disappear. |

Release mode is intentional for mutation execution: these changes violate the original after-condition assertions, and a debug panic would not demonstrate the requested observer discrepancy. Full actual row differences are retained in `final-v2/MUTANT-DIFFERENCES.json`.

The ten source bindings identify full actual native bodies, not translated substitutes. The wrapper supplies zero/one-next callbacks with success/custom failure and synthetic admitted enclosing masks. It is not a compiled production Firefox caller. `native/SCOPE.md` records the exact observation projection, provider families, callback and saved-state admission, and source translation limits. Unsupported numeric/string/hash/at-keyword provider controls emit diagnosed PANIC and are rejected; normal comparison requires clean diagnostics and exact row grammar. Ten Python-mode/shadow-import controls reject before unsafe imports/output creation.

## Predecessor renderer correction

The earlier NestedDriver maps `)` to32 and `}` to128, while native constants assign `}`32 and `)`128. Its renderer also omitted `{`2. The new driver uses all seven actual bits. Both authenticated predecessor debug/release traces have **91 rows with stop bits always0**, so their prior finite observations remain valid. New outer-parenthesis, outer-curly, square and overlap fixtures exercise the formerly untested values. `native/RENDERER-CORRECTION.json` and retained exact predecessor inputs establish this scope; mathematical byte-list ownership theorems remain unchanged.

## Boundaries and retained development failures

This closes a finite native/model calibration gate, not universal token-provider refinement, callback termination, real caller construction, UTF-8 codec, machine arithmetic bounds, all parser metadata, allocation/lifetimes or browser behavior. Line/column fields and exact parse error kinds are not in this projection. Progress, native delimiter law and admitted callback histories remain the root theorem's explicit premises. No positive raw trace is promoted into a universal proof.

The first driver compile lacked Inhabited for a diagnostic-only fallback; its failure log remains. The first integrated replay passed native/model and all six mutants but rejected its negative control because `#eval` printed PANIC on stdout rather than stderr. The checker now examines both diagnostic streams for expected negatives; ordinary model diagnostics/extra rows remain rejected. The complete fresh corrected replay passes. There was no change to root's theorem or retained production sources.

`HANDOFF.json` pins all owned source inputs and the unchanged root model. Completed owned compiler outputs are removed with path/size/hash inventory in `CLEANUP.json`; command logs, raw comparisons, generated source, diagnostic controls and final receipts remain replayable from the source capsule.
