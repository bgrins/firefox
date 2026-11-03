# CSS verification continuation 187

Continue formal verification and native/browser investigation to find observable CSS/Stylo defects. Each accepted repair belongs in a local native fix plus WPT commit, with research separately preceding it. User pushes; no Try or submission.

## Current evidence

HEAD e86b64866cdc, tracked tree/index clean (8769f5). 157 committed repairs; four separately validated uncommitted repairs and a cancellation-handoff candidate. Last ordinary signing attempt V126 failed in 1Password/Git128 and restored state. No new signing availability evidence; no bypass.

Continuation186 completed four cost runs (192 valid observations), existing traversal-statistics capture (10016 visits both variants, compute_style entries10012 broad versus6 selective), cancellation8/depth4 comparison (four failures repaired, eight passing signatures and two endings preserved), and composed selective font-unit14 (all14PASS, prior signatures/ending preserved). Exact runtime and receipt pointers are in sealed continuation186.

Both candidates retain the separate late CSS-animation startup46px failure despite root32/plain64. A non-font target class update repairs46→64 while preserving CSSAnimation object identities. KeyframeEffect identity is unmeasured. Source/interpretation notes d613d4bf/373bf9f0 separate construction, root-metric publication, task delivery, conversion and sampled-rule installation. No native cause is proved yet.

## Active work

1. Prepare artifact-only diagnostic source atop exact selective source8c89/e86. Record existing root publication/full traversal flags, returned ancestor-font hint and post-join signal, target normal-restyle admission, animation task delivery and already-computed conversion values. Dedicated logging flag; no new getter, flush or value recomputation. Root reviews, captures current state and runs local build. Agent typed_demand_review owns preparation only.
2. Refresh the canonical raw-index observation from completed selective native runtime50f72d25/audit980506c8. Canonical9515590f records36b15e; actual latest build raw4f9978 has unchanged semantics. Reuse the executed bounded raw-refresh workflow. Agent easing_servo_compile_plan prepares; root alone executes and verifies.
3. Prepare the shortest existing local publication path: font-unit three-path fix first, selective three-source/two-WPT parent delta second. Reuse existing publisher where its predecessor/source guards apply. Research, benchmark and traces stay outside native commits. Agent easing_source_review identifies concrete messages/diffs/requirements without source/index/signing mutations or new generic frameworks.

Root owns live source, app, index, canonical controls, builds, browser and signing. No active native build/browser/server at turn start. All eight completed experiment profiles were removed (275377981B); preserve required archived applications and incremental objdir. Existing untracked WPT/prototypes are retained and not blindly deleted.

## Next after preparation

Execute the reviewed raw refresh, then bind a fresh trace capture/owner to actual current state. Build the logging candidate locally and preserve shared source/application. Reproduce late46/46/46→64 with logging before interpreting order. If no post-publication conversion reaches the target, narrow scheduling; if conversion reads23 after publication, inspect provider/context timing; only trace downstream rule installation if64 endpoints were already assigned before the stale read.

Do not infer FinalAnimationTraversal from AnimationOnly, claim exact cascade-call reductions from compute_style counters, or increment defect counts from failing subtests. Preserve parent font-metrics/rollback work and root-self controls. Goal stays active; previous continuation made runtime and source-analysis progress.

## Raw refresh complete

Actual029ee4/session19339/561470/0 refreshed only raw_index_observation.current36b15e→4f9978. Resultb4f39221; newcanonicalepochc0c849f1aaacf9d666726e402b46ee5febdaaa103fd5e0dc4f8c4880f2519aa9. Independent04c9ce/session52392/686a3c/0 verified complete state/source/app/flags/controls and no semantic index change; rootbc50f0 read report. Raw-refresh runtime now sealed; native trace capture may use this completed lineage.

Mach reviewer selection1dd85c/session14351/fa7d3e/0 returns Herald #firefox-style-system-reviewers; logc453e09b. Initial sandbox call failed before operation at mach.lock, then authorized escalation succeeded. No new signing attempt.

## Root self-reference preservation

Unchanged root-self-reference14 ran against the selective archive using the executed font14 runner with only four policy fields adjusted (fixture/roster/runtime/settings), no new runner. First40efaa/38505/5a6c40 failed at harness importpsutil, WPT64/no tests; preservedv1. Mach WPT environment repaira5e8d6/24642/2145db/0 verifiedpsutil7.2.2. Retry3ec79f/60531/0d0255 owner0/WPT1 completed7PASS7knownFAIL. Independent74256d/24827/d64cfc/0 proved all14full normalized callback signatures andoneOK ending match original; archive/staging/process/temp preserved. No root-self fix claimed.

Startup source trace6d6c56bc sealed; root finalpatchreview0ba327, captureimplementationreview896e4d. Actual freshcapture3b503e/session75776 is running; poll it, no native install until actual capture/rootreceipt. Native owner adaptation pending actual capture. Single-late diagnosticfd87da44 retains exactly the late callback and stored-data observer for later log correlation.

## Diagnostic native execution active

Fresh capture3b503e/session75776/b1144d/0 completed:3183ce10490965a96a6680ab164260d8c674b974b24d8975468cd3256b6397a8. Root2668e6 verified snapshot==actualrefreshPOST and all8livebasehash/inodeclaims; terminalf5ae9146301067ab196aed7e5a1247b2c9096219767fdf25e1d2e630bc1eb0d5.

Native owner disabledmanifestd70dcc4e passed savedc19bdb/35586/25c099/0, peer6bf6ab/ac0e1c and public009532/68961/ed6d7b/0. Root reviewed08e962/5dd66b, ownpublicc1103a/28678/eaa4f0/0 and manifestconsumera91590. Activation8a1b46 changed onlytwoexecutiongates, preserving disabledpreimages; active0eef6144415a2e0cb278cb285bd8f93c82ebff53e4b410f840588636307b7645, consumer0d6516 passed. Actual03008b/session62755 is RUNNING, PID=PGID43798; poll this handle and do not mutate live source/app/index or start another native job. Last inspectione95fc1 found backup/PRE artifacts and trace not yet installed; no terminal or build result claimed.

Eight-role independent audit prepared disabled097e51e2 at css-root-font-startup-trace-root-audit-v1; future terminal/result/archive bindings remain null. Root binds only after actual ownerterminal/restoration. Logging absent during cancellation8 smoke; later single-latefd87da44 archive probe sets MOZ_ROOT_FONT_STARTUP_TRACE=1 and preserves stdout before close.

Font/cancellation publication packe0592ce4 and strict after-font publisherbbd0d3c5 are prepared; user was asked asynchronously whether1Password is available, no reply at this point. Next research checkpoint selection being prepared without incomplete runtime/futurecurrent/signing claims. No signed commit yet.


## Completed diagnostic build and late-start trace

Startup trace owner03008b/session62755 completed977710/0. Native build succeeded, cancellation8 passes with one OK ending and logging disabled. Independent audit2d63ad/session39179/f877f7/0 verifies source/app/index/flags/controls restoration, all owned process groups absent, backup removal and exact retained archive. Runtime sealed d72df27a; retained app css-font-unit-candidate-7sd29999.

Single-late logged browser run reproduces46/46/46 then64 after background-only target restyle; root32/plain64, original23/11 with no animations and same paused CSSAnimation objects. Full archive/fixture postcheck passes; profile34,801,363bytes removed. Trace contains actual root32 publication, selective normal handoff and child EffectProperties delivery; same effect address converts46 then64 with changed=1, and later64 with changed=0. Do not call this missing recomputation. Next: exact source review of downstream animation application and final traversal scheduling, then focused native tracing if necessary. JS phase boundaries and lifetime identity are not directly traced. No new repair accepted;157 committed repairs unchanged.

V127 research checkpoint disabled selection prepared; final trace closures and actual raw-refresh/current bindings pending. Signing availability unanswered. Compile agent preparing minimal raw-index refresh from the completed trace runtime; source agent reviewing final traversal scheduling; typed agent independently interpreting trace. Root retains all source/app/index/browser ownership.


## Completed raw refresh and downstream scheduling lead

Raw-only refresh761647/session25987/e149b6/0 changes canonical raw4f9978 to5a1822; epoch2927fa02. Independent verifiera7bdbc/session4423/8ccc6d/0 proves full preserved state; runtime sealed a0c2e94f. Source/app/Git semantic state and controls remain preserved. Diagnostic late runtime sealed98f7bc02 and independent causal review700b31a1.

Exact source review identifies a bounded queue hypothesis: StyleDocument has one drain between first and second traversal; changed effect properties can request animation work during second normal traversal, when PostRestyleForAnimation defers to a later PreTraverse. Existing trace proves64 conversion/delivery but lacks queue/pass ordinals, so no causal repair accepted. Queue-trace capsule adds env-gated logging only to EffectCompositor and ServoStyleSet, preserving the existing eight-role trace; type/context review and independent peer precede source seal and next build. Fresh capture-v2 must retain EffectCompositor canonical identity and add only ServoStyleSet as a fourth additional claim.

The scoped Lean extension separates endpoint revision from installed animation revision; normal visitation alone must not imply a ready observer. A stable finite queue and genuine termination premise are required, not an arbitrary fixed pass budget. New model and diagnostic remain research. After the next completed trace, add all closed artifacts once to V127, capture current state and attempt configured signing normally; no bypass/push.


## Queue-trace preflight and formal application boundary

Endpoint/application model0c5e1c01 passes16 axiom audits and6 false controls; root read complete model/source-map229791. It proves current-endpoint coverage through accepted histories and readiness after stable finite drain, and exhibits complete normal visitation with stale installed46 after endpoint64 refresh. Native queue simulation and convergence remain open. Extractor-v2 seals14389455 and recognizes18 extra logging events with separate pointer namespaces; no inferred phase/lifetime relationships.

Ten-role logging source a433f953 and disabled audit7ebf5f42 are prepared. Capturev2 faileda2077b/96823/a01cc7/1 before output because source_preimages incorrectly treated ordinary ServoStyleSet as canonical. Corrected v3 changes category data only; existing observer/ownership bodies unchanged. Actual v3 capturec2b784/83429/aa4b51/0 outputs8a70783e; root303e52 confirms exact completed-refresh snapshot and all ten live hashes/inodes. Root successful terminal872f63f6; free46.52GiB. Failed recordec1e94fc remains retained. Root preliminary envelope check8b338f failed only before writes because it read SOURCE-ROLES envelope instead of its roles member;8c15db confirms snapshot equality, and303e52 is the corrected successful root check. Native owner remains disabled pending exact actual-capture admission/public checks.


## Active ten-role native queue trace

Root reviewed final owner81198053 and exact admission/check deltas (13 other production bodies unchanged), actual public checka228f2/78717/14cfd9/0 and consumer. Activation1d1a08 changes only two execution gates; activecbed9b9e. Root active consumer9dfb21 failed missing required CLI digest before work; corrected1f737a/0 passes exact1907 input map, original failure log retained.

Actual native owner39b753/session89935, PID=PGID51543, root log css-root-font-startup-queue-trace-root-run-v1.log. It exclusively owns source/app restoration. Do not start another native/source/index operation while live. Logging environment is absent for cancellation8. Independent disabled audit7ebf5f42 reviewedff54a8; actual terminal/result/archive bindings await completion. Root next step: poll this same handle, audit completed restoration, then run unchanged single-late fixture on retained queue-trace archive with logging enabled.


## Verified wait after successful ten-role build and smoke

Build command actualexit0/errornull/groupabsent; build-RESULT inspected353f35 and final wrapper184f0b confirms browser_build_performed/command_success/preservation_verified. Build wall52s; known mach monitor export KeyError remains in full log, actual build successful. cancellation8 actual outcomes9afe1e are8PASS/0FAIL; archive provisional records now exist. Owner39b753/session89935 remains confirmed live atc56261; no terminal/restoration result yet. Do not treat provisional archive as browser-authorized or start another source/native/signing operation. Next samehandle poll, bind actual completed root terminal to disabledaudit7ebf5f42, execute audit with logging absent, freeze runtime, then exact single-late trace with extractor-v2 and depth probe3749adf6.

Root reviewed depth probe330fb4: four animated/literal ×depth2/4 cases,32*2^depth oracle, leaf-first observation/order and post-restyle CSSAnimation/KeyframeEffect identity checks; literal comparator not assumed passing. Browser outcomes pending. V127 final-addition plan a738151e reviewed187f78; include completed depth preparation with final closure. No new native acceptance or commit; goal remains active and this batch is substantive progress plus a verified wait, not blocked.


## Completed queue trace and depth evidence

Ten-role owner39b753/89935/c8b228 exited0; independent audit2cff5c/96854/f5c8e9 exited0. Sources/application/index semantics/flags/controls restored, groups absent, backups removed. Owner runtime8d8c3809 retains archivei_oiigf9; eight smoke callbacksPASS/oneOK.

Single-late trace49a25c10 reproduces46/46/46 then64 after a background-only restyle. Raw log explicitly shows pass2 changed64 endpoint conversion, same-target Layer request posted_before0/skip0, actual post-deferred(pretraverse0), document exit and repeated no-root calls; later PreTraverse selects posted child. This supports queued work surviving the final pass, not missing endpoint conversion. Exact JS phase/native installation still uninstrumented. Independent analysis being sealed.

Depth runtime8ff92544 extends to literal and animated roots at2/4levels. All leaves22 initially and after twoRAF/calibration. One background restyle repairs depth2 to128; depth4 reaches88 rather than512, with intermediate sequential values differing by mode. Same animation/effect identities and root32/plain64 controls. No fixed extra-pass repair or convergence proof accepted. Source design reviews both StyleDocument and separate StyleNewSubtree/FinalAnimationTraversal.

Raw-only refreshcb8409/9844/92fe3b/0 and independentverify37d731/88385/4fcd4f/0 completed. Canonical raw5a1822→7cda48; epochb06bcf21, all remaining state preserved. No native acceptance increment;157 committed fixes. Next: close bounded V127 research selection using completed evidence, fresh capture then normal signing; continue staged-drain/termination design without delaying completed-work checkpoint. Browser profiles69,488,827bytes removed after identity/process checks. Everything remains local.
