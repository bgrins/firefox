# Relation to held font work

The new diagnostic concerns a CSS font-size animation and relative margin in the same keyframe effect on one ordinary target. The font-only CSS and matching WAAPI controls distinguish this observed configuration. Readiness and reseeking do not resolve the captured discrepancy; an unrelated normal style invalidation does.

The earlier certified-path assessment and its inspected producer/dependency fixtures concern producer-local descendant handoff, repeated dependency draining, root/ancestor font providers and transition retargeting. Those nearby mechanisms may be relevant, but the inspected fixtures are not an exact duplicate of this same-effect case. This limited comparison does not establish a new root cause or independence from held #160; no old runtime is rerun and no extra bug is counted. Current built source includes the local stack, so no upstream/release attribution follows.

Inspected prior evidence: css-root-font-certified-path-validation-assessment-v1/README.md, css-root-font-certified-path-validation-pair-v1/FIXTURE-OWNERSHIP.json, css-root-font-drain-reporting-inputs-v1/font-animation-drain-producers.html and css-root-font-deferred-drain-wpt-v1/root-font-animation-dependency-settlement.html.

A later investigation should isolate the native path or compare a deliberately chosen source baseline before declaring whether this belongs to the existing held repair. The explicit changed-font getter conformance test remains independently actionable.
