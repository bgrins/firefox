# Late root-font queue trace

The ten-source diagnostic archive reproduces child font 46px immediately, after two animation frames and after calibration; root is32px and plain2rem is64px. A background-only target class change produces64px with the same root and child CSSAnimation objects, one animation each, paused at progress0.

The captured trace records child64px endpoints rebuilt during outer pass2, followed by a same-target animation request deferred during Servo traversal. StyleDocument returns, then two calls report no restyle root. A later PreTraverse selects that target. Detailed independent queue analysis is separate. Endpoint conversion and target selection are observed; installed animation values and exact JS/native phase timestamps are not instrumented. This is diagnostic evidence, not a newly accepted fix or universal convergence proof.

Root authenticated all8326 archive files before/after, exact fixture bytes and completed independent owner restoration. Browser session closed; configuration reset to installed Firefox without launch. Full output copied before and after close, with prefix check. Owned profile inode verified, process absence checked and34,744,235 bytes removed. Loopback server terminated normally. No source/app/index mutation by the browser run.
