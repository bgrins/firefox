## Current priority: contextual infinite-value rounding and consumer admission

The current local app preserves literal-NaN rounding. Its 24-case numeric baseline
completed 16 PASS and 8 FAIL across 72 calibrated snapshots; only a relative
`1em` step resolving to zero failed. The separate admission baseline passed all
eight constant-result cases across 32 calibrated snapshots. Direct contextual
values remain rejected by four easing consumers. These local results differ
from the retained Firefox 158 system-browser observations.

The archived numeric proposal is held, uncompiled and unexecuted. Its admission
regression is predicted from source, not observed in a candidate run. Next compile and rebase the contextual consumer representation against the
existing keyframe/dependency handoff, migrate infallible callers, and validate
admission/readiness before opening parser guards or attempting native promotion. The completed inactive representation
groundwork is archived here; integration, compilation and browser validation
remain unfinished. Preserve the accepted finite Round repair (145), infinite-step
guard (144), and latest generic source `df7e6932`; never restore older source
snapshots over them. The shared provider prototype remains held.

There are still 144 accepted fixes and 145 tracked IDs, with 120 excluded. No fix
146 is allocated and no formal coverage is added. Completed observations,
limitations and next steps are summarized in
`artifacts/css-local-signing-20261028-v43/README.md`.

---

