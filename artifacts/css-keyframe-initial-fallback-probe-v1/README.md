# Registered initial-value provider investigation

After the keyframe substitution repair, a five-case animation diagnostic still
shows `var(--missing, initial)` switching discretely:10 rather than12, while four
controls pass. That diagnostic is retained as an artifact, not a standalone WPT
repair requiring the keyframe predecessor.

A separate six-case ordinary-style WPT exposes the same uncomputed-initial-value
provider: a registered <length> initial1in serializes as1in rather than96px for
both inheritance modes after a CSS-wide fallback, and for inherited direct
initial. Three controls pass. This path does not call the keyframe conversion.
Native provider/initial-readiness review and candidate repair are pending.
No new committed-fix count increment is claimed.

`INITIAL-OBSERVATIONS.json` and `ORDINARY-OBSERVATIONS.json` retain classifications,
exact rows and scope. The tests/logs/raw JSONL remain separate. These are shared
local macOS observations, not isolated upstream runs or a complete formal proof.
The source/spec proposal is `../css-keyframe-csswide-map-audit-v1/`; its broader
same-effect dependency lead must not be conflated with this provider defect.
