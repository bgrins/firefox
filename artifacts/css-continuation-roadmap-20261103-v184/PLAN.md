# CSS verification continuation 184

## Goal and previous turn

Continue formal verification of CSS/Stylo to find observable bugs. Keep each accepted native fix with its WPT in a reviewable local commit, research separately, and maintain the fix ledger. No push or Try. Previous goal turn was **progress**: completed instrumented full34 and four isolated browser runs, proved the normal-entry gap in Lean, prepared a concrete native candidate, and completed a raw-only state refresh with independent live verification. The signing failure does not block investigation.

## Current authoritative state

- Branch stylo-bloom-verification-2, HEAD e86b64866cdc5e2260ba9be08c45756fd96e21bb; 157 committed repairs.
- Four validated uncommitted repairs: typed recascade taint; selected-fallback taint; font-relative keyframe invalidation; root animation identity including SMIL. Cancellation scheduling remains a candidate, not an accepted fifth repair.
- Configured signer failed the normal V126 attempt. Do not retry without evidence of availability; do not bypass signing.
- Canonical epoch90ac2cf3a7076cc8fc0a97f96cf8e6dd1c635102148a0d64d2490c772570cab8, raw indexf2be91fd818e483050d1662fa5ff5b9104aaa8d731daae89d67b86b4ccac29f1. ROOT rechecked HEAD/epoch/absent lock in df3a20. Original source/app restored. Native authority remains e86/085f capacity receipt.
- Actual raw refresh runtime css-root-font-cancellation-trace-raw-index-refresh-runtime-1 sealedc18b0d9757981fc8be3743c8cb9f4afdb832bc51bb2274c1bea8b17b5bd6f2b5; execution34a442/72752/16a5b4/0, independent live verification59db90/85375/1cc7fd/0.

## Cancellation evidence and next native experiment

Instrumented archive /private/tmp/css-font-unit-candidate-wf_yupqa/Nightly.app is independently verified; archive/restoration runtime sealed5bf9d6ad. Exact original34 function134dbede yielded the identical full report as the uninstrumented candidate:34cases/68samples, valid controls. Runtime sealed6ff66cc8. Four fresh-profile isolated cases sealedb2943303 reproduce child and root-pseudo no-read64/64px, root-read46/46px, expected46px. All native stderr retained; profiles removed after process absence; connector reset. Full PRE/POST source/app/archive/index/flags/control equality passed.

Both child histories restore root23 during AnimationOnly, then normal root entry is false with localhint empty, normaldirtyfalse, animationdirtytrue. The successful root-read control constructs its target animation after provider restoration; it is not normal delivery evidence. Existing-style animation processing skips EFFECT_PROPERTIES during AnimationOnly. Retained descendant hints need a reachable normal route.

Entry Lean refinement sealedc3d2864c: seven theorem audits and five rejecting controls passed in1a5e11/40313/e6cc86/0. Arbitrary extra dispatch cannot repair denied entry. Its normal-scheduling invariant composes with the earlier route induction; actual native establishment/forwarding/delivery remain unproved.

1. Execute the fresh bounded capture being prepared by easing_servo_compile_plan. It must use strict original-native whole epoch/snapshot equality modulo raw bytes, actual refresh receipts, and all fresh live checks; no historical recursive replay. Roles: traversal.rs, gecko/traversal.rs, glue.rs. Gecko traversal requires the ordinary additional-source claim.
2. Build and run the unchanged eight-case WPT against conservative route-only candidate css-root-font-cancellation-normal-handoff-fix-v1 (sealed6e00efb6). Three Rust files directly on e86; no logging or pending membership prerequisite. New atomic handoff records fresh child font work in AnimationOnly; after workers join it adds only RECASCADE_DESCENDANTS to the traversal root. Keep source/app backups and restore after the experiment; retain verified candidate archive for exact34.
3. Run exact34 on that verified archive. No-read child/pseudo must become46/46, six WPT controls and full34 calibrations must remain valid. Root-self bugs remain separately classified. Passing the gate alone does not prove endpoint rebuilding; use scoped trace only if needed.
4. Compare the selective alternative from easing_source_review before choosing a landing form. Broad descendant recascade on every qualifying animated font change may cause excessive work. Selective post-join child seeding needs the separately validated font-unit membership/admission repair; document and validate that dependency explicitly.
5. Add fixed-font intermediary depths1/4 with unchanged getter ordering (supplemental WPT being prepared by typed_demand_review), then baseline/candidate comparisons. No unrun fixture is a demonstrated regression. Examine non-root publishers, generated/flattened routes, and no-font/no-descendant controls. Fresh final-animation signals are currently suppressed before this handoff sees them; do not claim that boundary fixed.
6. After selecting and validating the native repair, refine the model to the actual scheduling/forwarding mechanism. Keep native correspondence limitations explicit. When signing becomes available, fresh research checkpoint then separately packaged fix+WPT commits with cumulative validation and ledger updates.

## Other retained work

Parent font-metrics arithmetic still needs its bounded native check. Rollback investigation has a coherent e86 A+B+D source rebase (b50eddbe) and a separate C memory/provenance design review (4106a370); baseline replay precedes candidate acceptance. These do not add accepted fixes. The 157-entry grouped catalog remains valid; pending section there is historical.

Keep required baseline/candidate apps and the shared objdir. Remove only verified owned obsolete scratch/build outputs/profiles/backups. No broad untracked-test deletion. Previous detailed evidence and failures are preserved in continuation183.

## Supplemental source review

Root6cdc65 reviewed the selective four-file cumulative patch and its explicit font-unit prerequisite: post-join ancestor-font seeding for styled root children, normal dirty root only when seeded, no added root-self hint. This preserves ordinary conditional recascade and still conservatively visits the subtree. No native/performance equivalence claim. Root8c9526 reviewed depth fixture delta; sealed61d91092 authenticates four callbacks (depth1/4 x none/root-read), wrappers fixed/styled before disturbance, original first+settled sequence unchanged. All baseline/candidate executions remain pending; initial8/full34 validation stays first.

## Fresh current capture completed

Actual capture2654a0/session40083/dcc6e4 exitedzero, output1554fc6b84d80e0a3bad3f608d7b3f00eb4bbc72c9b4ecc7e2f2c2279e91ae84. It used bounded direct saved-state equality and fresh Git/source/app/index/control checks. Root verified complete snapshot equality with the actual refreshPOST, current control bytes, all three candidate base hashes/inodes, and exact additional-source set (plain traversal plus Gecko traversal). No source/app/index mutation. This actual receipt is now available for the concrete route-only native owner.

## Original baseline provenance confirmed

Independent63cf62 traced ORIGINAL8 e8576aa8 to the actual bare-e86 archived original, not the font-unit candidate. Original archive buildID20261102193406; build receiptb504fd13, snapshotb8ba7f9b, actual full22 run74d6b3/28745/8142d8 (owner0/WPT1). Raw cancellation projection exactly6PASS2FAIL/oneOK; unchanged fixture93fee1d1. Source preimages outside the old three-role receipt are independently checked e86 object hashes, not invented old receipt fields. Full archive PRE/POST equality retained.

The concrete native owner is being prepared at css-root-font-cancellation-normal-handoff-candidate-browser-v1. Its archive helper must stop labeling glue unchanged: glue is a candidate role, while the snapshot records the actual non-role context projection (including base data.rs and uninstrumented matching/C++ context). Existing build/restore safeguards and exact original8 comparison remain.

## Native route-only experiment launched

Disabled owner f8a64acb (45payloads) and external publiccheck receipt96ec1876 authenticate. Root reviewed helper deltas3a6685/69aea0; both lifecycle/run and baseline/finally are unchanged from the executed trace owner. Saved full validation0c3d3e/session10516/7e4d5c/0 and scopedpeer1855f0/656731/be7537/bc952a passed. Public --check and exact flat consumer51f0f1 passed. Root preserved disabledPOLICY/FILES, activated only two gates in8e3a4f, and active flatconsumer13a605 passed.

Actual native run0a51bb/session64506, PID=PGID25379, active manifest605d4d2fecac431cc3c46132834be4321ec385cf0f0e3f751e048ba0a72fcf8d. Launch record css-root-font-cancellation-normal-handoff-root-launch-v1.json; log css-root-font-cancellation-normal-handoff-root-run-v1.log. Poll this handle; no duplicate owner, source/app/index change by another agent, or archive launch until actual terminal plus independent audit. Expected runtime css-root-font-cancellation-normal-handoff-candidate-browser-runtime-v1. No native outcome yet.

## Preflight routing failure before compilation

The actual native owner failed naturally0a51bb/session64506/10cf72 exit1 before runtime creation. Root read1cdb99 showed native baseline.require_role loads policy.capture_owner then calls adapter.require_role; the new capture adapter aliases that name to the executed native owner's router, which resolves the same capture_owner again. Actual logacbbb9 confirms979 repetitions and RecursionError. Fresh capture itself had succeeded because its observer received the old policy pointing to the existing leaf checker. The saved public --check did not exercise this new-policy live-admission route.

Root attempted a targeted stop only after identifying the concrete recursive call path;7b9626 found PID25379 already absent, so no signal was sent. No native source/app transition or runtime creation occurred. Active owner/capture remain immutable. Independent complete current-state/source/context/app/extras/binary/flag/control preservation verification9f23b0/session32590 is running. Retry needs a successor with the real leaf role checker and an actual saved-role invocation under the new native policy; do not substitute another top-level binding test. Reuse the current capture only after that independent preservation result passes. No Firefox fix increment.

Independent failure preservation verification9f23b0/session32590/35ddcb exitedzero. Result79c8e2e8 proves whole snapshot, all controls/flags, three source identities and context hashes, full application/extras inventories and binaries exactly match actual1554 capture; group25379/runtime/lock absent. Failed run terminal2ec45b6e remains immutable. No SIGINT was sent because the process had already exited. The existing actual capture is reusable after this evidence. Rootfa265d identified the real non-routing capacity role checker in the older exercised trace-current-capture-v1 baseline; successor should call that authenticated leaf directly and exercise the entire new-policy role-check entry point in saved tests.

## Resumed after grouped fix readout

Readout revalidated all 157 unique catalog commits as HEAD ancestors (33186e); no repair-count increment. That status turn did not advance the native experiment. Fresh inspection2b81ee confirms successor v2 was absent and all prior agents idle/completed, so root resumed compile agent on the concrete leaf-routing correction, source agent on the final-animation boundary, and typed agent on the three-role independent audit adaptation. No duplicate native job was started. Failed v1 and actual preservation receipts remain immutable. Root reviewed conservative/selective native deltas and prior archive audit; its hardcoded unchanged glue projection must become all context pins minus candidate roles.

## Corrected native attempt launched

Root9a204e reviewed explicit leaf-routing replacement and actual new-policy role invocation. Disabled v2 seal0f92976c authenticated44payloads in0f080b; saved582d69/77742/277a30/0 and external publiccheck7b7deb/55443/1c26ae/0 passed. Peer6b3c52/55b040/8aef85 subsequently confirmed1,309refs/15origindiffs/11testedinputs, with only baseline/check code changed. Rootc42fb9 preserved disabledPOLICY/FILES in root-activation-v2, enabled two gates, and passed active flatconsumer. Active manifest a442f78d9a6640f7a97ad7545f0d52b541aa5c60bf3b998270eace0a5a718f1b. Actual launch ef947a/session96261 PID=PGID26333, root-run-v2.log/root-launch-v2.json. Expected runtime now normal-handoff-candidate-browser-runtime-v2. Poll this session; no duplicate launch. Root reviewed independent audit's minimal three-role/context-minusroles diff b51c3f; bind actual outcome only after terminal.

Source review identifies FinalAnimationTraversal as StyleNewSubtree's second-pass boundary; existing cancellation fixtures do not establish coverage. Agent is preparing a simultaneous initial CSS root-font/child-rem case, still unexecuted and not accepted as another defect.

Actual candidate build completedexit0 with owned build group absent (b1e764). Unchanged eight-case WPT completedexit0,8PASS/oneOK/no unexpected results (root47bb6f raw/result/log read), versus original6PASS2FAIL. Owner ef947a/session96261 remains live while archiving/restoring; do not bind terminal or run archive before completion/audit. This validates the targeted observation only, not selective equivalence, performance, full34, or final-pass boundary. Supplemental final-pass fixture sealed72e920d5, source3c5a30/0/peerCLEAR, three callbacks; root4da8d1 reviewed source and read ordering. Browser execution remains pending.

## Native comparison and full34 completed

Owner ef947a/96261/022c3d exited0. Actual terminalca8eb2b9; independent audit8bf198/38751/b6b38d/0 reported40f6577f, whole restoration and retained archive verified. Runtime sealed25ca83c0e45c69a5c8232f633193dbf65eaa866c4508204ce335453a6d06b385. Retained app /private/tmp/css-font-unit-candidate-q42fzypj/Nightly.app. Buildexit0; WPT8PASS/oneOK versus original6PASS2FAIL. Owner removed1,008,605,176byte backup.

Exact134dbede probe on that verified archive completed34cases/68samples, allcontrolsvalid/noerrors/cleanuptrue. Exactly existing-child and root-pseudo rem/em-cancel/no-read changed64/64→46/46 (expected46); other32 numerical pairs unchanged. Rootidentity defects remain. Probe runtime sealedf4147b390fc1c7250ee04d83221b7bcf747519ab2e176960923d323d6838ff86; PREf3dad3/37810/752328/0, POST636fe9/17648/1bfc3d/0, complete snapshots equal. Browser closed/reset, profile34,575,288Bremoved00bf48 afterabsence. This is progress: actual native evidence supports model's normal-entry diagnosis. Landing form/performance/selective comparison and depth/final-boundary tests remain open; no new committed repair.

Next execution state: canonical90ac remains unchanged; completed owner observed rawf2be→36b15e826846a6c2136ff8d4b63744d844585dcb9efbd059a35534a95a62541c with unchanged semantic index. Compile agent preparing bounded raw refresh, then selective four-role capture/native experiment with explicit font-unit prerequisite and corrected role leaf. Typed agent preparing minimal genuine WPT setup for depth4+initial/final3 against retained original/route archives. No root native/browser process remains. No new signed commit; prior signer failure remains unresolved, no bypass/retry.

## Next continuation: selective/depth/final validation

Previous goal turn classified progress: actual native8/full34 and independent preservation changed next action to selective/deeper comparison. Fresh679203 rechecks HEAD e86/canonical90ac/no lock and actual terminal/raw records. Root b80519/db5921 reviewed minimal raw-refresh diff and full transaction. Saved6f9b88/44833/371c2d/0,peer2cc8f2/8dee95,publicdaaffa/0 passed. Disabled57e0e7ad authenticated, only execution gate enabled981a5d, activeec4502b0. Actual refreshd48c63/session79270 running; poll same handle before independent verification/capture. Typed preparing seven-callback genuine WPT run setup; source agent refining Entry model for both concrete handoff strategies with correspondence limitations explicit.

Raw refreshd48c63/79270/0ff211 exited0; independent verification4b3c7d/84064/9f3225/0 proved whole current snapshot==PRE/POST and epoch differs only raw observation, sources/app/binaries/flags/controls preserved. New epoch9515590f1e1f5adea96c1b736e9f583d9fa7c94d0562479a1835d29f5c06f05b, raw36b15e826846a6c2136ff8d4b63744d844585dcb9efbd059a35534a95a62541c. Runtime sealed341c3fa829e9a6b48ff69ec4144833f906b71e02ae5dc32fe0f8b8d2aa202888; actual resultc6bfb0ea12091e5c71e7a19c469d61b7c95c2341183c1542aeca9dd17d63d00a. No native fix increment. Selective capture can bind these actual receipts.

Supplemental genuine WPT completed: originalcb90f3/98857/593ca2 owner0/WPT1,3PASS4FAIL; candidatea2ab0b/52940/44a564 owner0/WPT1,6PASS1FAIL. Independent auditf0ff47/40900/2a063a/0 verified both archives/resources/process cleanup. Original runtime2e0f6fd1, candidate db9640ce. Broad fixes both depth no-read cases and initial numeric WPT, leaves late first46vs64. Unchanged-page standalone diagnostic sealed08c2b255 records initial46/46, literal64/64, late46/46 with post-target root32/plain64; initial WPT PASS is environment/timing-sensitive. Browser/server closed, profile34,647,413Bremoved and archive/staged resources preserved0399b7/28298/359145/0.

New handoff-entry model sealed01cd010b, actual2b684a/62281/d07af1/0:14audits/8falsecontrols,onlypropext. Rootfc7ce8/ca6f0c/855239/77aa31 reviewed source/mapping/authenticated76payloads and audit output. No native delivery or final-pass proof. Source note8edde4fe distinguishes signal/route from effect delivery.

Actual selective capture0af7d5/15831/194c92/0 completed after all browser work. Captured dc6557a3,terminal468c0989. Rootaf16bb verified full snapshot==refreshPOST/current controls/fourrole sourcehashes+inodes;free47.63GiB. Compile agent preparing selective four-role owner; no root process live. Continuation185 is now the active plan.
