# CSS verification continuation

Continue local observable CSS/Stylo bug finding, scoped formal verification, and independently reviewable native fixes with WPTs. Keep research in preceding commits; do not push or bypass signing. This roadmap supersedes the in-progress descriptions previously recorded in this unsealed draft.

## Current state

HEAD is signed font fix 334937d9ef8537e95cb80b29295797bc78f44252, directly after signed research 2701dc46ac5920adf3505885c67936287e1b037f. The immutable inventory css-current-fix-inventory-20261103-v1 records 158 committed primary repairs; FILES 99dd0a4a12faa64398b630894f30398a4144ea76ebad4fbfa07004c2b0c631f7. Pending candidates, held fix120, research and test-only commits are excluded.

Font installation completed 37f23e/session63623/5608c4/0; WPT lint and manifest delivery completed 58db67/session67410/425116/0; signed commit completed 9262f8/session27895/e46683/0. COMMIT-RESULT SHA256 4104034e49f850156b2030eea1eeb483624d5805bb4c0d5179cd6cf86a55d74f. Exact payload is data.rs, traversal.rs and root-font-unit-invalidation.html. Prior native61 validation covers the patch; delivery did not rerun a browser. Shared installed browser was not rebuilt.

Canonical epoch is c4c473042271fe7cf6ae58b8ea0dd6c597b20a3545178dbee864ceca142312f8. No live publication owner remains from these completed operations. The previous summary-only goal turn supplied a requested inventory readout but changed no project state; this continuation resumes the available publication action, not a blocked audit.

## Immediate publication sequence

1. Finish disabled research checkpoint V128, with exact signed font authority and the post-font preservation snapshot. Review focused authority changes and unchanged private-index/signing/rollback tail. Include corrected cancellation publisher, completed runtime outputs, inventory158 and new formal/spec work. Root alone captures fresh current state, binds it, validates, activates and signs.
2. After actual signed V128 success, execute css-selective-cancellation-after-font-publication-v2 install, delivery and commit serially. FILES fd90151bffb93a7a4887e41c292a8b8a78601bdf4536c8d732edc1869a5eca99. Use actual V128 result as research predecessor, while PAIR-BINDING separately authenticates the font receipt. Check actual terminal results before advancing.
3. Record successful cancellation in a new inventory-v2 snapshot; preserve immutable inventory-v1. Do not increment the count before a native commit exists.
4. Prepare narrow publication bindings for the already validated typed-reparse taint fix, then the selected attr() fallback taint composition. Existing publishers require updated exact intervening font/cancellation history; historical browser validation must not be relabeled as a run of a new combined tree.

The first cancellation attempt c1608d/session39894/d0b47f exited1 before writes: gecko/traversal.rs was Git-tracked but absent from canonical pins, installed identities and OWNED. Earlier descriptions of it as canonically content-pinned were incorrect. Preservation capsule css-selective-cancellation-publication-install-failure-v1 FILES 8ddb0fd2a876ecfa0063abc21be0505d63888ff22fb00d6d534cc5c6c93e1da3 records unchanged source/app/controls and absent generated destinations. Publisher v2 admits only that exact missing source after HEAD/hash/inode checks; existing sources retain installed ownership checks. Its 21 rejection controls and independent review passed. The old immediate font-to-cancellation sequence is superseded: v2 requires one artifacts-only signed research child of font334.

## Formal verification and next observable experiment

Completed wave-chain model css-root-font-endpoint-wave-chain-lean-v1 (FILES1a2c480bbd9e6bd4470378e8dfd67437de947cf0af23bf88fcd745b8172c880b) has 15 axiom audits and six false controls. It proves dependency coherence after depth complete synchronous waves under a stable root and parent-only functions; no depth-independent fixed wave budget suffices.

Completed coalesced event-driven model css-root-font-coalesced-chain-lean-v1 (FILES60ceb366bd3ddb10162137e1346f0f560c165966128822ce65ed83798197eb59) has 27 axiom audits and six false controls. Refresh, queued and inflight obligations strictly decrease a weighted measure on enabled steps. Explicit finite settlement plus coherence yields expected chain values. Arbitrary idling, changing external inputs, trees, multiple dependency edges, and native scheduler refinement remain unproved. Native queues do not directly encode this model's generations or phases.

Normative trace css-root-font-keyframe-settlement-spec-trace-v1 supports dependency-first keyframe computation and application before CSSOM observation; it establishes no general native pass-count or cycle policy. Eligibility review records missing native reason/property/provider metadata. Neither proof establishes queue-empty implies correct computed style.

After validated publications, rebind and build css-root-font-startup-bounded-drain-diagnostic-v1 against actual current source. Its one 45-line C++ insertion permits at most16 additional selected-work traversals, without a destructive17th probe. It is diagnostic only: syntax/roundtrip checks passed, but no build/browser run yet. Compare late and initial depth fixtures, retain phase/order observations, and determine whether changed endpoints actually get applied. The initial-depth fixture does not itself prove native StyleNewSubtree entry.

Existing trace shows child64 endpoints queued during pass2 and selected only later. Depth fixture observes leaf22 before restyle, depth2 leaf128 afterwards, and depth4 leaf88 on the recorded getter. Later ancestor reads are sequential, not an atomic snapshot, and no final leaf getter follows them. Do not infer native wave counts from these values or claim an unrestricted loop/fixed third pass is a production fix. Root-self context remains a separate validated pending repair.

## Resource and ownership discipline

Root owns live source, browser, canonical state, index and signing. Agents prepare artifact-only research and independent reviews. Completed process handles are terminal; never restart a merely quiet live operation. Read actual receipts and current state before continuing.

Two completed diagnostic profiles were removed after process/inode checks, totaling69,488,827bytes. Retained candidate apps still support comparisons; delete old build targets only after proving they have no remaining use. No broad deletion of untracked WPTs.
