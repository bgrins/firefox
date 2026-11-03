# CSS verification continuation 186

Continue finding observable CSS/Stylo bugs through scoped formal models and native/browser evidence. Package each accepted repair as a local native fix plus WPT, with research separately preceding it. User handles pushes; no Try or submission.

## Current state

- HEAD e86b64866cdc5e2260ba9be08c45756fd96e21bb; 157 committed repairs, all distinct commits reverified as ancestors. Four separately validated uncommitted repairs remain: typed recascade taint, selected-fallback taint, font-relative keyframe invalidation, root animation identity including SMIL. Cancellation scheduling remains a candidate. Startup observations do not yet establish another distinct defect.
- The prior user readout refreshed ancestry/counts but did not advance the implementation. This continuation advances runtime evidence: four completed cost/correctness runs, independent assessment, application preservation and profile cleanup.
- No tracked worktree changes, no staged changes at turn start. Existing untracked research/native prototypes and WPTs remain retained. Last normal configured signing attempt failed; no bypass or retry without changed availability.
- Canonical epoch9515590f still records raw index36b15e; latest selective build observed raw4f9978f with unchanged semantics. A bounded refresh is needed before another native capture, not for archived-browser diagnostics. Original shared source/application remain restored.

## New completed evidence

Post-calibration observations sealed166341aa5f38ff6f61a55d90d08e12c7d88286ebd8f6b758de2a0f6f9658c771 were verified against every payload. Both broad and selective late-start cases remain46/46/46, including the extra target read after root32/plain64. Initial broad46 versus selective64 in this launch is not stable across earlier runs; no phase/regression claim.

Cost/correctness runtime `css-root-font-handoff-cost-runtime-v1`, sealedcd9ad56907df20e06300cc1fc26fe9d479a6df6311f5f0e99dda4cea2e023d60, ran the exact17cb2ee8 probe in fresh profiles broad/selective/selective/broad. All192samples pass, including48warmups and144measured. Counts0/1000/5000; both directions checked. 5000leaf per-run/per-direction medians broad1.5–2.5ms, selective1–1.5ms. Millisecond quantization, only two runs per variant, cumulative candidate differences and absent native route counts limit interpretation. Directional local evidence only; no browser-wide speedup claim.

Preparation7c6e2e/session75878/77408c/0 authenticated both full8326file archives. Independent assessment/preservation/cleanup60e8ae/session74216/c3651f/0 proved all calibrations and raw sample identities, PRE=POST inventories, and removed137507796B of four owned profiles after process absence. All browser sessions closed and connector reset to installed Firefox without launching it.

Existing counter source review `css-stylo-existing-profiler-counters-review-v1` identifies Styles marker elementsTraversed/elementsStyled (compute_style entries, including recascade/cache hits), aggregated across workers. They do not identify phases or exact cascades. Existing DUMP_STYLE_STATISTICS is a separate per-traversal diagnostic. Local profiler-cli0.5 is older than the profile-analysis skill's0.10 requirement; no profile analysis or manual profile parsing performed.

## Next work

1. Package the font-unit admission repair first (data.rs/traversal.rs plus its14case WPT), then selective handoff as its parent delta (traversal.rs/gecko/traversal.rs/glue.rs plus cancellation8/depth4 WPT). Saved comparison, exact combined font-unit14 and cost/counter checks now pass. Research remains outside native commits. Validate any changed installed predecessor separately; these archives are e86-based, not an arbitrary later source stack.
2. Trace the separate CSS-animation startup path. The non-font target update repairs46→64 with the same CSSAnimation objects. Follow root-font publication and full traversal flags, post-join signal, target normal traversal, actual EFFECT_PROPERTIES delivery and endpoint conversion. Only trace downstream rule installation if64 endpoints were already assigned before the stale read. Agent interpretation/trace plan373bf9f0 is ready; no native trace applied. Refresh the raw canonical index binding before any new native capture.
3. Preserve root-self controls and the independent root-identity repair; do not conflate startup failures with cancellation or inflate the defect count. Initial results remain launch-sensitive. KeyframeEffect object identity was not measured by the browser diagnostic.
4. Parent font-metrics arithmetic and rollback A+B+D remain retained pending native checks; held120 excluded. Commit completed work when configured signing is available; preserve the user's signing setup. Last signing attempt failed, and no new availability evidence arrived in this batch.

## Formal scope and retained resources

Latest Lean handoff-entry extension01cd010b passed14new audits and8false controls. It proves normal-entry obligations under explicit signal/child/forwarding/budget premises, not native signal publication, hint retirement or final-animation completeness. Prior exact receipts remain in continuation185 and sealed runtimes.

Keep original baseline, font-unit-only, instrumented, broad q42fzypj and selective olt9f9lz archived applications and shared incremental objdir. Completed browser profiles were removed; no broad deletion of untracked tests or targets. Active work is artifact-only agent preparation; no root native/browser/server process remains after the completed cost run.

## Saved comparison completed

Root11e0c1/0 completed cancellation8/depth4 comparison: exactly4target FAIL-to-PASS changes,8unchanged PASS signatures and2unchanged OK endings. d43db2/0 authenticated raw logs against sealed manifests and equal authored fixture bytes. Peer f658cf/3b84bf/63f77d/8ec011 scoped CLEAR. Artifact `css-root-font-cancellation-saved-comparison-v1` sealed2495f8f9c80629b3174f8ab2d043942a73a0a897908bf36c70d6397d0f1803cc. Combined font-unit14 remains the next correctness gate.

## Existing traversal counters completed

Statistics runtime `css-root-font-handoff-statistics-runtime-v1` sealedae649ef36c98f2a065e89148595398eebe7087ae0df173a04bf3c3d24c5e0471 records broad/selective seek1000→firstchild64 with valid initial/post controls. Four captured blocks each; traversed10016both, compute_style entries10012broad versus6selective, reuse9988versus0. This supports avoided styling entries, not an exact full-cascade reduction or phase identity. No profiler or native instrumentation. Full archives preserved; two profiles68632164Bremoved after process absence; all browsersclosed/reset. Combined font-unit14 runner now prepared disabled and under peer review.

## Font-unit14 and startup discriminator

Selective font-unit14 actual3c7cc0/session66109/700520/0 passed14callbacks andoneOK; roota7a700 verified complete archived preservation and process/temp cleanup. Activationdc1aa5 changed only execution_enabled, preserving disabled flatmanifestda0e90dc; activeefcbb30d. ROOT-TERMINAL saved5a0913. Independent full14 prior-signature comparison is being prepared. Initial root activation schema assumptions9e2480/e1367c failed before any mutation; corrected against actual flatmanifest85693f.

Target-class diagnostic runtime `css-root-font-target-restyle-observations-v1` sealed93316759c0d9711f1b17e003777f2dee9ddd046152fe113ad003e565bad26210 now shows both late46/46/46→64 after a non-font target update, with same root/child CSSAnimation objects/counts and pausedprogress0; root/plain32/64 andbackgroundrgb1,2,3 verified. Initial broad64/selective46→64 remains launch-sensitive. Native source-chain d613d4bf distinguishes effect construction, Device publication, update conversion and final rule installation. Next native trace should determine missing/early post-publication UpdateProperties delivery; do not assume the exact cause from browser observations.

All browser sessions/server closed, both fullarchives preserved,69238021Bprofiledata removed by actualpostverifya546a4/57053/5e9e55/0. Current tracked diff remains empty22b54b. No new committed or accepted defect; goal remains active.

Identity precision: independent review720662 confirms the successor measures CSSAnimation object identity, not animation.effect identity. The sealed runtime README phrase "same target/effect" should be read as the same target and CSSAnimation; KeyframeEffect identity remains unmeasured. No separate effect-identity claim is supported by this fixture.

## Batch closure

Font-unit14 independent audit5b23a1/30191/2da851/0 passed; root706d8d read actual successful output. Exact14orderedPASS signatures andoneOK ending match prior font-unit candidate; full8326filearchive/stagedtrees/process/tempcleanup verified. Runtime sealed2e0c909cf69f2364845684bcaeabce7526dccbf78a90f9489e8ef80ab95f095c. All experiment browser/server processes are closed, source/index unchanged, and275377981B of eight owned browser profiles removed this batch. Active native/accepted-fix count remains157committed plusfourseparatelyvalidateduncommitted; cancellation candidate packaging is next, with separate startup trace prepared. No new native commit or signing attempt. This continuation made concrete runtime and source-analysis progress; goal remains active.
