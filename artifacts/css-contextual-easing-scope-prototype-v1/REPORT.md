# Selected keyframe scope transport prototype

This eight-source artifact successor combines the closed-guard easing handoff with selected-rule scope transport. Bases come only from signed5d9487828523 objects and immutable handoff captures, not a live compiler overlay. The exact handoff-v2 serde correction is included. Generic calc df7e and the separate tree-counting fallback implementation are unchanged. No native build, browser, index, epoch or app mutation was performed.

## Transport

The new scoped non-document visitor preserves callback order and eligibility. The old visitor projects away scope and keeps its document-applicability boolean. Containing shadow, own shadow, assigned slots and containing part trees remain in that order; SVG-use normalization and part/export eligibility stay unchanged. Own shadow rank includes every assigned-slot hop. Slot rank decrements per hop, not callback. Part rank increments per containing edge, including absent intermediate rule data; document fallback retains its actual positive distance. Existing rank saturation remains.

lookup_keyframes_with_scope returns the existing first winner plus CascadeLevel; the old API projects away that level. Author/document/user/UA fallback order is unchanged, and user/UA retain their origins. No element-relative scope is cached in shared KeyframesAnimation.

The owning cascade dependency pass saves/restores context.scope and selects the declaration guard with scope.guard(guards), retaining the non-inherited-property save/restore. Gecko assigns selected scope to its fresh Context and keeps its existing global shared-lock guard. Servo threads selected scope into generation, sets its fresh Context and uses the origin-selected declaration guard for timing, composition and declarations. Both keyframe computation sites therefore use the same selected level as dependency recording. The API remains fallible and all parser guards remain closed.

## Open boundaries

Existing animation-name lookup lacks the reference's declaring root and is explicitly best-effort. Preserving that winner does not prove normative tree-scoped name selection. Same-name collisions need separate reference-root work; proposed tests use unique names.

Counting every part edge differs from the current collector's increment placement when intermediate data is absent; this is deliberate physical-root transport, not claimed collector equivalence. Exact root reconstruction beyond finite rank saturation is not established. Existing SVG-use normalization is retained without asserting that raw get_shadow_root_for_scoped traversal matches every anonymous-tree case.

Current Values5 requires zero for failed tree-scoped tree-counting references. Native fallback one is owned by counter's separate repair. This patch does not change it or allocate another count. Outer-part contextual tests require that repair plus contextual parser activation before they can pass.

Selected-step effects, complete style-sharing/effect invalidation, animated-input/self-dependency ordering and Web Animations API context policy remain open. A consistent scope is necessary but not complete lifecycle readiness. Root's first six-source check failed unnecessary serde derives; those were corrected separately. No root retry success is inferred here.

## Candidate tests

Four future-activation WPT cases cover same-tree versus outer-part keyframe easing, each with sibling-index and sibling-count. Declarations/effect stay installed through sibling prepend/restore. A separate structurally identical holder calibrates index/count; the target has no ordinary contextual property that would independently mark its sibling dependency. A constant part rule is installed once; no per-phase unrelated normal declarations force restyles. Captured easing and opacity at750ms are compared to literal WA controls after all phases are recorded. Known parser rejection fails instead of skipping.

These tests have not run and do not distinguish ranks -1/-2 or +1/+2. SCOPE-CONTRACT lists exact root-identity postconditions for nested slots/missing data/document fallback. Native root identity and privileged UA/user guard tests remain required. No native-equivalence model or duplicate proof package is claimed.

Independent bounded source review c3d2fd found no new concrete transport blocker; revised fixture review50b93b cleared the separate-holder/sibling-only design. Root reviewed the scope draft b27a9b. Existing expected-failure WPT coverage records outer-part/nested animation-name lookup gaps (counter cf80e1/00aabb); no new discovery is claimed. Own-shadow rank determination adds a slot-chain walk; no performance-neutral claim is made.
