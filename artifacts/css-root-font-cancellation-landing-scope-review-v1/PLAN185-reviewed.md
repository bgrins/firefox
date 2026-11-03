# CSS verification continuation 185

Continue formal verification of CSS/Stylo to find observable bugs, with independently landable local native fix+WPT commits and separately committed research. Keep work local. No push/Try. Previous goal turn was progress: broad native8/full34 completed with independent preservation. This continuation adds genuine supplemental WPT, persistent late observations, a scoped Lean refinement and fresh selective-build capture.

## Current state

- Branch stylo-bloom-verification-2; HEAD e86b64866cdc5e2260ba9be08c45756fd96e21bb. 157 committed repairs. Four separately validated uncommitted repairs: typed recascade taint, selected-fallback taint, font-relative keyframe invalidation, root animation identity including SMIL.
- Cancellation scheduling remains a candidate with demonstrated targeted improvement, not an accepted additional fix. Do not count the initial/late test failures as separate bugs without root-cause separation.
- Configured signing failed the last ordinary attempt. No bypass or retry without evidence of availability. Native/source/app and index mutations remain root-owned; agents artifact-only.
- Canonical epoch9515590f1e1f5adea96c1b736e9f583d9fa7c94d0562479a1835d29f5c06f05b; raw36b15e826846a6c2136ff8d4b63744d844585dcb9efbd059a35534a95a62541c. Completed refreshd48c63/79270/0ff211/0, independent4b3c7d/84064/9f3225/0. Runtime normal-handoff-raw-index-refresh-runtime-1 sealed341c3fa8. All semantic state/source/app/flags preserved. No active root process, browser or HTTP server.

## Evidence that drives the next experiment

| Test | Original | Broad route-only candidate |
| --- | --- | --- |
| Cancellation WPT8 | 6 PASS / 2 FAIL | 8 PASS |
| Exact34 ordering probe | Existing-child and root-pseudo no-read64/64 rather than46 | Those two pairs46/46; other32 pairs unchanged; all calibrations valid |
| Depth1/4 cancellation without root read | Both fail64 rather than46 | Both pass; explicit-root-read controls also pass |
| Initial simultaneous root32/child2rem CSS animation | WPT first46 rather than64 | WPT pass, but unchanged-page standalone46/46; environment/timing-sensitive |
| Pre-styled23 then simultaneous root32/child2rem CSS animations | WPT first46 rather than64 | WPT first46; standalone first46/settled46; post-target root32/plain64 controls |

Broad native owner-v2 completed ef947a/96261/022c3d/0; independent audit8bf198/38751/b6b38d/0. Native runtime sealed25ca83c0; retained app /private/tmp/css-font-unit-candidate-q42fzypj/Nightly.app. Exact34 runtime sealedf4147b39. Supplemental original runtime2e0f6fd1 and candidate db9640ce independently auditedf0ff47/40900/2a063a/0. Standalone stored-observation runtime08c2b255 preserves the distinct launch environment and read chronology; it adds no style getters. Neither initial PASS nor46/46 identifies the native final-pass branch. Root/plain calibration occurs after both target samples.

## Formal scope

Handoff Entry extension sealed01cd010b4dd005afb810c9cb582db9b3f6b509788e28c196be1ef02c27705191 passed14new audits and8genuine false controls in2b684a/62281/d07af1/0, using onlypropext. Root and peer reviewed exact source/mapping/logs. Broad local-descendant hint and selective styled-child plus normal-dirty marking satisfy their respective normal-entry obligations under explicit signal/child premises. Admission is not visitation; forwarding and a sufficient dispatch budget remain premises. No proof of atomic publication, native hint lifetime, effect delivery, provider freshness or final-animation completeness.

## Immediate work

1. Selective native build and cancellation8 succeeded; exact34 matches all68 broad-candidate numerical samples, with valid controls and complete PRE/POST preservation. Native runtime50f72d25, probe runtime d3b53bdc. Original/shared source and application are restored; no native or browser process remains. Candidate archive is /private/tmp/css-font-unit-candidate-olt9f9lz/Nightly.app.
2. Supplemental selective5PASS2FAIL is independently audited5c6776/8054/3d0273/0 and sealed runtime f0aff0f0e92c399d67419aaa637849996149325876464254ed4459f3a499a8a2; its minimal policy package5f6df10d retains the unchanged runner/resources and10binding differences. Both startup cases still first46vs64; all depth cases pass. Source agent is preparing the minimal extra target read after existing root/plain calibrations, preserving the original first/settled pair. Run this in matched broad/selective launch environments before deciding on scoped native instrumentation.
3. Run the prepared cost/correctness probe17cb2ee8 (packageee70c14b) against broad and selective archives with matched fresh profiles, retaining every sample. Root read the perftest guidance; no timing run yet. Invalid reports cannot support timing conclusions, and profiling is needed to attribute any difference to avoided cascades. No CI/push.
4. Startup diagnosis remains distinct from cancellation acceptance. If calibrated late values remain stale, trace actual root publication/traversal flags, post-join signal/root, normal target recascade and EFFECT_PROPERTIES delivery. Do not infer FinalAnimationTraversal from AnimationOnly or a numerical result. Broad recascade already forces target recascade after a successful handoff; selective-only effects must be interpreted against the actual path.
5. Choose and package a reviewed native fix+WPT with explicit font-unit prerequisite handling; research separately before it. Update accepted-fix catalog only on acceptance. Commit completed work when configured signing is available; no bypass. Parent font metrics and rollback work remain retained.

Canonical epoch9515 still stores raw36b15e; completed selective native execution observed actual raw4f9978f1aa4ba73721b0405270f7dabce9727a72ec842b654a833cd37f57abb3 with unchanged semantic index. Independent audit/full34 already account for this. Any further native capture requires a bounded raw-only refresh from the actual selective runtime/audit first; archive-only diagnostics do not require another build.

## Retained work and cleanup

Parent font-metrics arithmetic and coherent rollback A+B+D rebase remain pending native validation; held120 remains excluded. Keep required original/font-unit/instrumented/broad apps and shared objdir. Broad native backup1,008,605,176B removed after restoration; latest diagnostic profile34,647,413B removed after process absence. No broad untracked-test deletion. Earlier exact receipts and failures are preserved in sealed continuation184.

## Selective native experiment started

Root5df1a3 reviewed the two code deltas (admission/check) and explicit font-unit prerequisite;13other production bodies remain identical. Disabled86a56563 authenticated45payloads, saved5e7135/68604/1be7d9/0,peer40077f/ecef1c,public005e3f/53885/7ba4f2/0 passed. Root1573f0 preserved disabledPOLICY/FILES, activated two gates and verified active flatmanifest758668de9e3bd6883d0f8b3cbad2dd79aa4d66f2b7e894a67037b8bc517b6772. Actual0741ac/session24023 PID=PGID32895 running; root-run-v1.log/root-launch-v1.json under selective-handoff prefix. Poll this handle; no concurrent native/source/app/index changes. Independent four-role audit prepared disabled495a8dc8, future bindings null.

Actual selective buildexit0 with build group absent (3cfab2). Unchanged cancellation8 completed8PASS/oneOK/WPTexit0 and complete assessment48d269. Owner0741ac/session24023 still archiving/restoring; do not bind a terminal or use archive yet. Cost probe prepared sealedee70c14b, exact JS17cb2ee8,48checked samples at0/1000/5000 fixed-font leaves; root828809 reviewed source and limits. No timing run yet.

## Selective native and exact34 completed

Owner0741ac/24023/15ffdd exited0; terminal66480071. Independent audite183e4/31282/789629/0 verified980506c8; native runtime sealed50f72d25bb9bea8f03da9357259f54f17ad2121d363c6f8b7d89621db507c8b4. Retained app /private/tmp/css-font-unit-candidate-olt9f9lz/Nightly.app. Buildexit0,8PASS/oneOK,originalapp/source restored,backup1,008,605,176Bremoved.

Exact34 on selective completed with every numerical pair equal to broad candidate, allcontrolsvalid/noerrors/cleanuptrue. PRE4317be/55487/5479f7/0 and POSTc4994c/34028/4f666e/0 are equal; profile34,575,366Bremoved. Probe sealedd3b53bdcf921a75e6856b06323b00e0a9f00d772fee5f014c975892da00e9f2c. Supplemental selective actual6ea4dc/session51558 nowrunning using unchanged prior runner/resources with only10 actual archive/authority/runtime policy fields changed; no duplicated runner. Policy hash57133bb2, unique selective supplemental runtime.

Supplemental selective6ea4dc/51558/59b78a owner0/WPT1 completed5PASS2FAIL: both initial and late CSS-animation first values46vs64; literal-root and all4depth callbacksPASS. No regression claim from initial broadWPTPASS because its separate standalone run alsofailed46/46. Selective does not resolve startup merely by adding font-unit membership. Root322efd inspected exactcallback rows/result. Source agent preparing one-extra-target-read diagnostic after existing root/plain calibrations, preserving earlierfirst/settledsequence.

Native selective raw observation advanced36b15e→4f9978f1aa4ba73721b0405270f7dabce9727a72ec842b654a833cd37f57abb3; canonical9515stillholds36b15e. Full34snapshot verification adjustedraw locally and proved stateequal; no canonicalrefresh yet. Required before any next native capture; not a source/index semantic change.
