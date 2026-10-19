# Stylo verification bugfix commits

Local branch: `stylo-bloom-verification-2`. No fixes have been pushed or submitted.
Each fix is one standalone commit containing its Gecko change, regression WPT,
and any necessary test metadata. Research, proofs, tooling, and this index stay
outside those commits. Full commit hashes are the management identifiers.

Current checkpoint: **59 committed fixes; the accepted queue is fully committed.**
Repairs with incomplete review are excluded from this count.

<!-- CURRENT-SIGNED-QUEUE -->
## Signed commit queue

Full hashes below are the current management identifiers. Earlier evidence records retain their historical hashes and signing status. Each native fix includes its WPT; proof/tooling commits precede it. See the [machine-readable ledger](CURRENT-COMMITS.json) and [original queue check](../css-signing-resume-20261019/ROOT-COMMIT-CHECK.json) and [Ahom commit check](../css-ahom-lf-partition-probe-v1/ROOT-COMMIT-CHECK-v1.json).

| Repair | Native + WPT commit | Proof/tooling commit |
| --- | --- | --- |
| color-missing | `82b254686378e57711759c238b975cdf4678a287` | `a75f70c97b155b46b3820be79fe4b41e272f7b8d` |
| color-zero-prefix | `591b3e12567865c7e047530753e510c54d18b3db` | `519f2b2a756969dbba9c45415d2b40506560d94d` |
| transform-deferred | `c9274972124198e8f8466ddcd667d1c23cb044ec` | `4c401192c6ae79b5a6c3b4328f939d70e2474be2` |
| clamp-nan | `a4fe7dd06fd7dac3924b2dc9aea4f57103eb1b98` | `7b2f125756a218c548cdd95d2693e5a022bbb61b` |
| mod-rem-infinity | `bfbce1cc7e9a5b53d5cc00317a265d7141428997` | `033c4ac60d396dd9dde7ce085b76edae15353696` |
| attr-numeric | `499c0c6b72ac4bc0a6396bffa3fa0d71665409ce` | `607a4fcfbab31bf37f2495b38c9841be83cbfc66` |
| logical-shorthand | `e27beeac5129d7331f8aca9babbe6bfc199d7d24` | `f5b175e01f2182d26ee2e137ca2072f60d185d4c` |
| grid-abspos | `7f5a1105253e60b283174ea890862b1943e8702a` | `739139c30e536e6ac655a4597bca14f3d97f8e06` |
| sigma | `8e78ffd376c4d478b5d614f568f3bf09d894ad8b` | `5dc0849a15e83215ae89fb809752014a3ba241f1` |
| sizing-stretch | `2a61f0b7433628e8a77159b968ca570632591b8e` | `4a696e8c980f4f5432cc31653fed0a327308c5cd` |
| query-attribute-wrappers | `16ff45a117b149ec95fc633c7ac18d8a1c38ca0b` | `3dc4259d2dd035c248512062d84eafd8bc1dc15b` |
| query-content-box | `ef3d32280505b7fb6c1b35989d7e74c56f1aee0a` | `dc96c3763a4d175db6539c57cf5ece7fcd4614eb` |
| table-span-spacing | `98fd7a22a32744ab429828d609cf5bfb3affc4a5` | `799efd5a456feaafaa905f91b6e7ef1c3a8aa0ee` |
| polygon-intercept | `06be3d7e722c55ffbff97e6be237bd39a4920295` | `1a86773b4a5ec6f53f5f0a0b7a6e35da06cf8a38` |
| stroke-reference-box | `96e0ad8c6a0ae58b9ce8c47579c9bc06f67fc1e2` | `b709247b5f33999576d743e0183d2d7867f18b7b` |
| object-fit-partial | `66fb24648a15769f80c2adf37030e68598dae68f` | `ff354bf3100dbe2cea2b83ab87dbee11793fbbe3` |
| abspos-auto-margin | `f67ddfaa3dc328d7359c7fca56e61a1249e1ee96` | `1c9e80b2228a27ed596e6865f510c9ab994f713b` |
| block-flow-collapse | `e09ffb35c0b47c6c29c43c64d887fb524b5e7423` | `8621e83c91428e627c710fcac796b2de8efae7a0` |
| bad-url-recovery | `83bc2bd3922697d44a602bf48902e821796a60e3` | `366b0542b5595614895a17e5e334019f0fcf5d20` |
| svg-empty-mask | `065183ac8449800f0dbef3c23a15be3863ca60ae` | `629771d9fd8c5b18782647a5b4d21e8e978d15b0` |
| image-zero-mask | `6bb2557507bcd6346664e539f9f4b9628d8e6078` | `c767ea97fb253ae03b852b095beca0b14f452948` |
| nesting-specificity | `c57d0c806d94c6e6dd56e23acdeed847c5ea1571` | `ab6513e805c725c11d3e61ffb82583123f209ee3` |
| scroll-fixed-anchor | `e606244c4546e522cf4a6e86dac98e216305003b` | `e0494649157d12b7d42b6e3f750ddcc81e2474fe` |
| text-overflow-line-state | `c348436003653a08b6766339d9e0c8f89084d062` | `e32b6ba35b6e09ea87f685ebbc09639669bc55a5` |
| tab-zero-intrinsic | `eca9efde2991b5a458d23efd1c6d33d58fdf4a77` | `ba9ebc9d81b7e8ac2fa25ac58425ee0f76c151f5` |
| font-threshold | `9da730d5ebd6cb59a0a5b2a666d6679808d58889` | `153b0e8d9bf36a49b3575629371cf5c0a0d81db6` |
| timeline-pseudo-axis | `0af700c67a5aef6048b19b72350320cd1fe82346` | `5388c30dc8ec99a5b0016580aaa59ce6849142bc` |
| font-priority | `9cca10125782ebe2bf076a5e5d8becdacae5ff16` | `0cafb33759540c5f6b794312351b3315b1590235` |
| root-rlh-zoom | `43afd2c6f3500cee4a2dd07d07eb14aca723fae3` | `635b8995326d0c8ca526bc9aea8d8cc7d295d2c7` |
| animation-composite | `6b8dc654e8d017562533308571af23c3099fd5cc` | `7ee385b8404b0e332950ae4e4edaf4a1bb3e20a2` |
| text-emphasis-pua | `bbf5a4095f85fb250ea442695a311f2547ffdc19` | `75401fe2983110104c3f0a3bef1686d807701033` |
| negative-ligature | `8ee543a6ff23cc097f54f1c3e984f7d5f7e56fea` | `3f61a60e15b32e88afdf5975fd65b49fd760d568` |
| complex-utf16-ahom | `39ce7571a61097a80d5bf07adbc3ae48a2f0262e` | `28d9e8cc1065d7b00e3d891b42049c82d5e7058c` |
| worker-font-removal | `32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` | `07dc1d27343268a8add266605c33fc5f966ef155` |
| hyphenation-coordinate | `18871240dc7d077bf223822013e7a50cf581e2d1` | `a1eed2e249aed69af41142c5a55e49a5d88fbb2e` |
| attr-namespace-cache | `3aa7d25635ff9dc3bc105269dd9b7b13b5f80cb0` | `adde61d9742f3f9939514bdfe10fde08a794aeff` |
| attr-invalid-entry | `fd9c07e1130bcb68684c25e7527f5b0ff3c3bd73` | `76bda27b8dfdb88ebdcb7e4706508688d0a3f064` |
| attr-fallback-preparation | `7822bb6d17b1381cdb3e56deb20c5ec3e078adec` | `31265260cc3daa2bbea93c237a9491b6f2afcaa4` |
| mathml-token-range-origin | `f843fd7568f30e14e664c37c36544d8d88e8c1bb` | `6eb5a90e3fa3b6128ddd6397d9dae9f1ab34b88d` |
| attr-typed-fallback-eligibility | `e3ba54f6f826fe265eb5bc4731f66f64465dd47c` | `30c8dfeb4b746104b53ad5bc6440c1d53734f570` |
| attr-noncustom-dependency-collection | `3892ab844694fedd987f5ce1dd2165f53fc2dbed` | `0db19774e6f2bf6692790459f8e6e54ca426e366` |
| resolved-unit-dependency-summary | `58200fa81a6f92f92a1898ba2866a2fbcbac0daa` | `03bad7f708329254a9af2073f0b4106ba557e914` |
| unit-token-classification | `26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` | `2e1f5f62c8a6325679a83adc7f637e104c488bf7` |

<!-- END-CURRENT-SIGNED-QUEUE -->

## Hyphenation coordinates committed

`18871240dc7d077bf223822013e7a50cf581e2d1` contains one native comparison and its WPT,
following companion `a1eed2e249aed69af41142c5a55e49a5d88fbb2e`. Two browser failures
become passes; all eight new checks pass and 20 existing results are unchanged.
Root's relocated native/model replay preserves 40,608 controls in both provider
variants and passes the 31-module guard proof. The full ownership and persistent
spacing-cache obligations remain open. See
[acceptance](../css-hyphenation-measurement-offset-probe-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-hyphenation-measurement-offset-probe-v1/ROOT-COMMIT-CHECK-v1.json).

## Worker font removal committed

`32ba35ffb9a17f5e91df5c56f01a06a452dfdc8a` contains only the four-line worker-family
rebuild and its WPT. Proof/evidence companion: `07dc1d27343268a8add266605c33fc5f966ef155`.
Four worker failures become passes; all 16 new checks pass. Nine existing files
retain 10 passes and one expected failure. Root freshly replayed the 18 Lean
list-model theorems and accepted the independent source/lifetime review within
its explicit provider, heap and concurrency limits. Discovery was static audit
and browser isolation, not Lean. Final WPT differs from the paired test only by
two spec metadata comments. The loaded-descriptor/provider repair is separate.
See [acceptance](../css-worker-font-removal-fix-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-worker-font-removal-fix-v1/ROOT-COMMIT-CHECK-v1.json).

## New native-verified patches

These are not yet signed commits or additions to the formally accepted count.
Each patch contains only the native repair and its WPT. Full proof/tooling
companions remain separate.

| Repair | Minimal patch | Landing constraint |
| --- | --- | --- |
| Cumulative rollback exclusions (A+B+D) | [fix-a-b-d-v1.patch](../css-layer-cutoff-composition-probe-v1/fix-a-b-d-v1.patch) | Coherent repair supersedes original A/B patches; 80 assigned cases pass without C |
| Logical/physical rule exclusion (C) | [fix-c-after-a-b-d-v1.patch](../css-layer-cutoff-composition-probe-v1/fix-c-after-a-b-d-v1.patch) | Follows A+B+D; final browser gate passes; local performance pair recorded; full source quotient remains open |

## Further counterexamples and repairs in progress

The full line-break provider proof found a supplementary Ahom/Thai UTF-16
counterexample that reaches browser layout: splitting a text node immediately
before a preserved newline suppresses an interior CJK wrap on the following
line. The final paired WPT has eight failures/305 controls before and 313 passes
after the narrow encoding/seek-width backport. Eight existing files retain all
46 passing checks; all paired source/binary pins are stable. ICU4X PR8144 already
structurally fixes this mechanism upstream; this is an old-version backport,
not a novel upstream defect. The three-file native/checksum/WPT patch applies
and reverses at historical HEAD/base. Lint and rustfmt pass. Independent exact
provider/full-breaker replay now passes from a fresh source-only copy. The
narrow backport is accepted and signed as `39ce7571a61097a80d5bf07adbc3ae48a2f0262e`,
following companion `28d9e8cc1065d7b00e3d891b42049c82d5e7058c`. Original language/LF
proof obligations remain open or refuted. Evidence:
`css-ahom-lf-partition-probe-v1/ROOT-SCOPED-ACCEPTANCE-v1.json`.

The expanded proof found a regression in important-inline candidate A: a
following outer `revert-layer` replaces its exclusion and revives a normal inline
physical alias. The 64-case WPT fails four cases on A+B+C. Removing A passes those
four but fails four distinct outer-value controls. The corrected implementation
preserves the intersection of origin, ordinary-layer and important-inline
cutoffs in constant space and passes all 64 cases. Related A/B/C tests pass
16/16/72 cases; existing tests retain six passes and two expected cycle failures.
All browser runs have stable source/binary pins. **Do not land A v1.** Independent native review and root replay of 24 Lean modules support the
correction within the recorded source/model boundaries. A+B+D passes its 80
assigned cases without C, with existing results unchanged. The C baseline atop
that correction has eight alias failures and twelve additional D alias failures;
its 116 controls pass. The proposed stack is one coherent A+B+D repair followed
by C, which adds its 72-case WPT and the remaining 16 D cases. Earlier A/B approval and
patch applicability are historical scoped evidence. No accepted count increment.
Evidence: `css-layer-cutoff-composition-probe-v1/ROOT-NATIVE-WPT-v2.json`.

Logical/physical `revert-rule` rollback (C) now has a corrected stack boundary:
the A+B+D predecessor passes its assigned 80 cases; C then fixes 20 failures
across its 72-case WPT and the complete 64-case composition WPT. All 136 pass on
the restored candidate, with stable source/binary pins. Root verified the
five-file predecessor and four-file C patch apply in order and reverse exactly
at historical HEAD. Both contain only native changes and their assigned WPTs.
A local three-cycle StyleBench pair scored 525.69 without C and 532.91 with C
(+1.37%, higher is better); this is exploratory evidence, not a speedup or
statistical no-regression claim. Actual compiled Declaration size grows from
24 to 32 bytes. The block-pointer/normalized-priority quotient and complete
observer/evaluation composition remain open. No signed commit or aggregate
formal acceptance increment is claimed. Evidence:
`css-layer-cutoff-composition-probe-v1/ROOT-STACK-VALIDATION-v1.json`.

Full cascade proof work exposed an important-inline layer rollback discrepancy:
an outer normal part rule is wrongly excluded. A second counterexample shows
that an intervening revert-rule replaces an earlier cutoff and restores an
excluded animation. Separate 16-case WPTs each reproduce one failure with 15
controls on the corrected v2 baseline. Repair A alone passes its 16 cases and
leaves B's failure unchanged. B alone passes its 16 cases but exposes a second
A failure previously masked by cutoff replacement. Thus B applies independently
as source but requires A first to avoid an observable regression. The original two-patch layout was superseded by the coherent A+B+D
repair above; neither historical patch should be landed alone. Both patches apply/reverse exactly at base and HEAD.
Existing rollback tests are unchanged on A-only, B-only and both: six passes
and two expected cycle failures. The combined build passes all 32 new cases.
The earlier independent review accepted that limited A/B matrix; its replay
is retained as historical evidence and is superseded by the composition review. The missing-body original
draft remains a harness-error record; no new full formal acceptance.
Evidence: `css-rollback-compound-fix-v1/ROOT-NATIVE-WPT-v1.json` and
`css-shadow-context-order-proof-v1/rollback-candidate-review-v1/REVIEW.md`.

The extended scoped-reference ownership WPT reproduces four inheritance
failures with eight controls; twelve existing tree-scope cases pass. A light
descendant inherits a slot-root reference despite having no local root/slot
lookup path. Exact decoder replay and a specialized all-integer Lean theorem
rule out numeric rebasing alone with the unchanged decoder. Root identity or
equivalent provenance, lifetime and style-reuse handling are required before
implementing the sparse/inheritance repair. Evidence:
`css-shadow-scope-ownership-probe-v1/ROOT-BASELINE-v2.json` and
`css-shadow-scope-ownership-probe-v1/SCOPE-REPRESENTATION-v2.md`.

The hyphenation proof's complete native consumer extraction produced a
coordinate-sensitive witness. A dictionary/font-pinned WPT now reproduces two
auto+soft-hyphen failures with six controls and passing line-origin calibrations.
The one-comparison native repair now passes all eight cases. Twenty existing
tests retain nineteen passes and one expected failure. Source, font, dictionary
and metadata inputs are pinned across the paired runs. Its two-file patch
applies/reverses at base and HEAD, excluding the signed-ligature repair. Root
independently rechecked nine Lean coordinate/refill theorems; complete native
consumer composition and machine/font premises remain open.
Evidence: `css-hyphenation-measurement-offset-probe-v1/ROOT-NATIVE-WPT-v1.json`.

C10/C11/C13 of the full saturation composition scope are refuted on the frozen
saturation-only candidate by the rollback witnesses. The scope is preserved;
unaffected lemmas continue, and corrected combined sources will need explicit
binding and independent review. These new leads do not change accepted counts.

## Shadow cascade and line-break checkpoint

Configured signing retry 36738 again failed with the 1Password buffer error;
HEAD and the staged companion are unchanged. Signing remains enabled. Evidence:
`css-shadow-context-order-fix-v1/SIGNING-RETRY-v1.json`.

The shadow-order baseline has 26 failing and 118 passing new WPT subtests.
Failures cover exported-part important/layer rollback at depths 8–32 and
forwarded-slot important/layer rollback at counts 7–32. Ten existing regression
files retain 71 passes, two expected failures and one OK harness result.
The four-file native candidate widens the packed level to u32, assigns negative
slot ordinals directly and checks representability instead of aliasing contexts.
The build, formatting and independent actual-source boundary replay pass. All
144 new WPT subtests pass, fixing all 26 baseline failures; the ten existing
regression files are unchanged. Lint has zero errors and two ignored-WPT
warnings. The standalone six-file patch applies/reverses at base and HEAD.
Full C1–C13 formal production is now active; no aggregate acceptance increment.
Evidence: `css-shadow-context-order-fix-v1/ROOT-NATIVE-WPT-v1.json`.

A separate sparse scoped-name lookup probe has one failure and three controls;
its complete pseudo-map/provider design is frozen and is not folded into
the saturation repair. The expanded saturation-only pseudo probe has 12 failures
and 12 controls across depths 2/6/8/32, with all support and geometry calibrations
passing. Evidence: `css-shadow-sparse-pseudo-probe-v1/ROOT-SATURATION-ONLY-v1.json`. The newline consumer probe has no geometry or independent
expectation discrepancies across 1,440 calibrated fixtures. The raw partition
invariant remains refuted. Additional consumer proof work is approved without
changing that failed obligation. Full language and hyphenation caller proofs
continue. Accepted and committed counts are unchanged.

### Current acceptance and signing status

- Private-use text emphasis: root accepted the full v2 scoped proof after the
  independent review closed the earlier arbitrary-run gap and supplied missing
  original exhaustive executions. Three new and nine existing reftests pass;
  two baseline failures repaired. Separate eight-file native/WPT patch remains
  uncommitted. Evidence: `css-text-emphasis-pua-fix-v1/ROOT-FORMAL-ACCEPTED-v2.json`.
- Signed ligature advances: root accepted independent native/font/oracle and
  formal review. Four baseline failures repaired; all 48 new cases pass, with
  unchanged results across 26 existing files. Separate three-file native/WPT/font
  patch: `css-negative-ligature-fix-v1/fix-candidate-v1.patch`.
  Evidence: `css-negative-ligature-fix-v1/ROOT-FORMAL-ACCEPTED-v1.json`.
- Sticky auto-inset and writing-mode repairs pass independent native review;
  their full formal companions remain pending.
  Their four-combination build/WPT matrix passes; neither is counted above.
- Latest signing retry 41911 failed with the 1Password buffer error. No new commit
  hashes exist. HEAD and the staged RGB companion remain unchanged, with signing
  enabled. Evidence: `css-sticky-writing-mode-fix-v1/SIGNING-RETRY-v1.json`.

The sections below retain the chronological evidence and earlier checkpoints.

### Earlier uncommitted checkpoint — 18 October 2026

- Animation composite-only updates: 70 new and 340 existing subtests pass,
  fixing 52 baseline failures. Independent native review passes. Full formal
  review found required import-closure, consumer-cache and null-provider
  corrections; root replay confirmed the v1 review findings. Independent v2
  review closes import/null/restyle issues but still requires delivered-readiness
  and equal-setter cache preservation. Root rechecked the frozen review;
  Full v3 correction and independent review are now root-accepted after
  1,498-file authentication and recheck0, with the original scope retained.
  Evidence: `css-animation-composite-fix-v1/ROOT-FORMAL-ACCEPTED-v3.json`.
  Single native/WPT commit remains pending configured signing.
- Root `rlh` zoom: final isolated two-file patch applies at branch base and
  HEAD. Build and 34 new/28 existing subtests pass, fixing 15 baseline failures.
  Evidence: `css-root-rlh-zoom-fix-v1/ROOT-NATIVE-WPT-v2.json`.
  The v2 supplement closes the dependency-state gap. Root accepted full scoped
  independent review after authenticating 528 files and rerunning its checks.
  Evidence: `css-root-rlh-zoom-fix-v1/ROOT-FORMAL-ACCEPTED-v2.json`.
  Single native/WPT commit remains pending configured signing.
- Private-use text emphasis: isolated eight-file native/WPT patch; three new
  and nine existing reftests pass, fixing two original failures. Root accepted
  independent native review and approved the full formal scope, now in production.
  Evidence: `css-text-emphasis-pua-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.
- Percentage `shape-margin`: isolated four-native/two-WPT patch; all 306 new
  subtests pass, fixing 148 baseline failures. Twelve existing reftests pass;
  three expected failures remain. Build/format pass; root accepted the independent
  native review. Formal work remains. Evidence:
  `css-shape-margin-basis-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.
- Initial View Transition types: five duplicate-deletion selector failures
  reproduced with sixteen controls. Startup deduplication passes all 21 new and
  three existing subtests; isolated two-file patch applies at both bases.
  Root accepted independent native review; formal work remains. Evidence:
  `css-view-transition-types-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.

- Language-sensitive line breaking: the final three-file native/WPT patch fixes
  29 original failures; all 360 new cases, 48 existing subtests and two reftests
  pass. Immediate words use their own language, and Latin-1 buffering now updates
  language state. Root accepted independent native review and approved the full
  formal scope; implementation is active. Evidence:
  `css-line-break-language-fix-v1/ROOT-INDEPENDENT-NATIVE-v1.json`.

- Hyphenation policy ownership: six browser failures and 43 passing cases,
  including dictionary calibration, with dictionary/loader inputs pinned.
  Later inline limits affect an earlier whole word. Expanded coverage has
  54 failures among 289 cases; candidate passes all 289. Nineteen own-limit
  controls, 360 language cases, 48 existing subtests and two reftests pass.
  Separate five-file patch applies at both bases. Independent review then found
  a per-continuation style omission: four first-line/first-letter probes fail on
  candidate1 and all four pass before the repair. Candidate2's range correction
  passes 722 checks. Final candidate4 preserves offset guards and empty-range
  finalization; build and 722 checks pass. Lint has zero errors and three
  ignored-WPT warnings. Root accepted the collaborative native/evidence review
  after 762-file authentication and 66-live-pin recheck. Full formal work is
  active; no aggregate acceptance yet. Final evidence:
  `css-hyphenation-ownership-fix-v1/ROOT-NATIVE-REVIEW-v4.json`.
  Evidence:
  `css-hyphenation-ownership-probe-v1/ROOT-BASELINE-v2.json`.

- Contained quote append invalidation: expanded baseline has 12 failures and
  52 controls; candidate passes all 64. Fifteen existing tests pass and three
  fail as unchanged metadata expects. Build/format pass, lint has zero errors
  and one ignored-WPT warning. A standalone three-file patch applies at both
  bases. Independent review and formal work are queued; no aggregate acceptance.
  Evidence: `css-quote-scope-append-fix-v1/ROOT-NATIVE-WPT-v1.json`.

Latest signing retry (session98203) failed with the existing 1Password buffer error. HEAD and
index are unchanged; signing remains enabled. The RGB companion remains the
only staged change. No new commit hashes are assigned to the work above.

| Finding | Fix commit | Regression test | Status |
| --- | --- | --- | --- |
| StyleBloom clear loses evidence of earlier counter saturation | `d855b3483b493c7e596b5d1d30d613fa7b7e2db5` | `testing/web-platform/tests/css/selectors/ancestor-filter-saturation-crash.html` | Previously completed; standalone Gecko change and WPT crashtest |
| Recursive relative-selector Bloom construction overflows on deep subtrees | `93a062cded54c974dff03ce2618aaf612a9c8d61` | `testing/web-platform/tests/css/selectors/has-deep-subtree.html` | Previously completed; standalone Gecko change, WPT, and required metadata |
| False-supports import incorrectly establishes layer order | `5d3638a91adf7b662041e192d121c7fd91c86f0a` | `testing/web-platform/tests/css/css-cascade/import-supports-layer-order.html` | Verified: baseline 4/16 fail; patched 16/16 pass; committed |
| Important user/UA declarations retain normal layer order | `e28cb48d656ba83097fb0960734e4317252e7d81` | `testing/web-platform/mozilla/tests/css/css-cascade/important-origin-layer-order.html` | Verified: baseline 10/21 fail; patched 21/21 pass; committed |
| Nested scopes choose the first outer scope's inner root instead of the closest matching inner root | `075be5516374d31c55a1e0f71b3fa80591042503` | `testing/web-platform/tests/css/css-cascade/scope-nested-proximity.html` | Baseline 4/14 fail; patched 14/14 pass plus 86 existing scope subtests; committed |
| Shadow-host traversal reports an unmatched scope-end selector as a limit | `a46e5310cd604adff10e914e82e8a326b9fb7957` | `testing/web-platform/tests/css/css-cascade/scope-shadow-limit.html` | Baseline 6/9 fail; patched 9/9 pass; 58 subtests and scope-part reftest pass; committed |
| Scope root is treated as its own scoping limit, contrary to the April 2026 draft update | `78c11c75170af5480a88fd9682db41183760f652` | `testing/web-platform/tests/css/css-cascade/scope-root-is-not-limit.html` | Baseline 5/10 fail; patched 10/10 pass; 128 scope subtests, 8 focus/hover subtests and reftest pass; committed |
| Relative-selector result cache reuses scope-dependent :has() matches across different scope roots | `d4a2b600f078d4c29e6dd8e0f1668121941a64e5` | `testing/web-platform/tests/css/css-cascade/scope-has-cache-scope-element.html` | Baseline 7/13 fail; patched 13/13 pass plus 58 related scope subtests; committed |
| Filtered nth-index cache reuses sibling counts across different scope roots | `92c013c16908bd30593ca7385b24dad1be4288dc` | `testing/web-platform/tests/css/css-cascade/scope-nth-cache-scope-element.html` | Baseline 10/20 fail; patched 20/20 pass, 13 has regressions and four reftests pass; committed |
| Scope-limit changes stop invalidation inside a relative selector instead of reaching the enclosing rule subject | `64ac54569f1cc202172ded92ee23ba749cd3284e` | `testing/web-platform/tests/css/css-cascade/scope-limit-has-invalidation.html` | Baseline 32/40 fail; patched 40/40 pass, 131 total selected subtests; independent 138/138 mutation comparisons pass; committed |
| Filtered nth positions are not propagated when a relative anchor has a non-subject tail | `b1b1bacb9406d75f35648d40a70ce9ad0fc3ab69` | `testing/web-platform/tests/css/selectors/invalidation/nth-of-has-nonsubject.html` | Original baseline 5/8 fail; final expanded WPT 10/10 pass, 70 total subtests and two reftests pass; independent 130/130 comparisons pass; committed |
| Scope wildcard revalidation gives equal nth results for elements with different real filtered positions | `f4b34bf7fef125857979a210616d201e28eefded` | `testing/web-platform/tests/css/css-cascade/scope-nth-revalidation-sharing.html` | Baseline 10/20 fail; patched 20/20 pass, 103 total selected subtests and two reftests pass; 78 static comparisons and 960 mutation comparisons pass; committed |
| Relative-length round simplification loses negative zero with infinite steps | `708b914901eeb7a2d348855c2efcf099e6003317` | `testing/web-platform/tests/css/css-values/round-infinite-step-relative-length.html` | Six valid original WPT cases fail; final corrected 64/64 pass, 217 existing subtests pass with two unchanged expected NaN failures; committed; literal-zero prose conflict documented separately |
| Name-only container queries do not invalidate after ancestor name changes | `238710ff9db7f54449c075bf80c7c3d40b43387a` | `testing/web-platform/tests/css/css-conditional/container-queries/container-name-only-invalidation.html` | Baseline 12/12 fail; patched 12/12 pass, 26 selected subtests pass; committed |
| Saturated animation iteration indices alias infinity, lose direction, and suppress iteration events | `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1` | `web-animations/timing-model/animation-effects/current-iteration-large-and-infinite.html`; `css/css-animations/CSSAnimation-large-iteration-events.html` under WPT | Baseline 12/52 fail; patched 52/52 pass, 246 selected subtests pass with five existing expected failures; committed |
| Registered numeric calculations resolve direct font-relative operands before the own font is ready | pending | `testing/web-platform/tests/css/css-properties-values-api/registered-numeric-relative-units.html` | Known failure area; baseline 24/76 fail, substituted/absolute/length controls pass; candidate built, existing tentative font-consumer expectations under review |
| Variable-bearing shorthand cache reuses another declaration after partial revert-layer | `11482ee213bf63c749b6d205c2c7591d783bdaa8` | `testing/web-platform/tests/css/css-variables/shorthand-substitution-partial-revert-layer.html` | Baseline20/28fail; patched28/28pass,74total subtest passes plus2reftests,4unchanged expected failures; preceding proof/tooling `f32fc6f2831ebe0987c9f0e9003b4597e3bce019`; committed |
| Color conversion loses analogous missing RGB components before interpolation | pending signing | `testing/web-platform/tests/css/css-color/color-mix-missing-cross-space.html` | Known-WPT-failure rediscovery;81baseline failures become132passes;42existing failures also fixed; final gate1374PASS/412unchanged expectedFAIL/4OK; proof companion staged separately |
| Multi-color mixing skips zero-weight prefix state needed by a later missing component | pending | `testing/web-platform/tests/css/css-color/color-mix-zero-weight-prefix.html` | Baseline12FAIL/4PASS →16PASS; selected1134PASS/67unchanged expectedFAIL, build passes; rational fold proof/source binding accepted (17audits); signing pending |
| Eager transform evaluation replaces deferred percentage-dependent accumulation with identity | pending signing | `testing/web-platform/tests/css/css-transforms/animation/transform-deferred-composition.html` | Baseline9FAIL/4PASS becomes13PASS;206total WPT passes and5OK,676distance/SMIL checks unchanged; bounded22-audit proof and final independent review accepted; native/WPT-only patch applies independently |
| Clamp simplification discards NaN operands | pending | `testing/web-platform/tests/css/css-values/clamp-nan-preservation.html` |49FAIL/45PASS→94PASS; existing406PASS/2expectedFAIL unchanged; full candidate47audit proof accepted with explicit native bridge premises; signing pending |
| Mod/rem lose finite dividends with valid infinite divisors | pending signing | `testing/web-platform/tests/css/css-values/mod-rem-infinite-divisor.html` | Baseline12FAIL/36PASS becomes48PASS;315total subtests pass and3OK; bounded12-audit proof and independent terminal review accepted; native/WPT-only patch applies independently |
| Nested progress censors NaN before outer calculation completes | pending spec-history review | Focused WPT pending | Nested opacity expression returns.5 instead of0; top-level NaN, finite and equal-endpoint controls pass |

The import finding has normal and important manifestations, covered by one fix.
The origin finding covers both user and UA sheets, also with one fix. Its WPT is
Mozilla-only because installing these origins requires `SpecialPowers`; it still
runs in the WPT harness. It includes author-origin and stable-order controls.

## Evidence

- Import investigation: `artifacts/css-spec-lean/research/import-layer-investigation-20261017/REPORT-v2.md`.
- Origin investigation: `artifacts/css-spec-lean/research/origin-important-layer-order-trace-20261017.md`.
- New WPT baseline: `artifacts/stylo-css-bugfix-baseline-v2.log` and `.jsonl`; local Firefox build ID `20261016094926`. Binary and test hashes: `artifacts/stylo-css-baseline-inputs.json`.
- The first baseline attempt is retained as `artifacts/stylo-css-bugfix-baseline.log`/`.jsonl`; port 8000 was occupied, so that attempt is infrastructure failure, not bug evidence.
- Patched tests: `artifacts/stylo-css-bugfix-patched.log`/`.jsonl`; 66/66 subtests pass across both new WPTs and existing `import-conditions.html`. Exact before/after outcomes and hashes: `artifacts/stylo-css-bugfix-verification.json`.
- Both committed patches independently pass `git apply --check` against `32226ddf3a29d58a52291babebdff2a5a7ce46c6`; browser testing used the combined build. Patch files and checks are recorded in the verification JSON.
- Targeted lint: 0 errors, two warnings because ESLint excludes these WPT files. Explicit warning output: `artifacts/stylo-css-bugfix-lint-warnings-v2.log`.
- Build and lint logs: `artifacts/stylo-css-bugfix-build.log` and `artifacts/stylo-css-bugfix-lint.log`.
- Local server configuration: `artifacts/stylo-css-wpt-ports.json` (temporary WPT override removed after testing; no test expectation changes).
- Patched full CSS-model replay: `artifacts/stylo-css-patched-origin-replay-v1/verification.json`; 141/141 queries, 1,310 metadata readbacks and 21 controls pass. Independent supplement: `artifacts/stylo-css-patched-origin-review-v1/REVIEW-v1.json` (15 corruptions rejected). Historical disagreement evidence remains unchanged.
- Nested scope verification: `artifacts/stylo-scope-investigation-v1/verification.json`, investigation `REPORT.md`, and independent source/terminal review in `artifacts/stylo-scope-review-v1/`.
- Shadow limit verification: `artifacts/stylo-shadow-limit-v1/verification.json`; independent investigation in `artifacts/stylo-scope-root-limit-review-v1/` and patch/terminal review in `artifacts/stylo-shadow-limit-review-v1/`.
- Root-limit verification: `artifacts/stylo-root-limit-v1/verification.json`; intentional spec change and original WPT expectations retained in the same directory. Independent source, expanded nesting-test, lint, and terminal reviews in `artifacts/stylo-strict-root-review-v1/`.
- Follow-up invalidation probe (no new defect): `artifacts/stylo-scope-invalidation-review-v1/DYNAMIC-REPORT-v1.md`; six mutation cases, 18 states and 36 computed values agree with fresh DOM controls.
- Relative-selector frontier audit (no new defect): `artifacts/stylo-relative-frontier-audit-v1/REVIEW-v1.json`; 48 browser cases pass. Search hints were inferred from source; Bloom activation was not observed, and the accepted proof domain was not extended.
- Earlier Bloom verification: `servo/components/selectors/verification/NATIVE-STORAGE-CHECKPOINT.md`.
- Scope-sensitive relative result cache: `artifacts/stylo-scope-has-fix-v1/verification.json`;
  independent investigation and patch review in `artifacts/stylo-scope-has-independent-v1/`
  and `artifacts/stylo-scope-has-patch-review-v1/`.
- Scope-sensitive nth indices: `artifacts/stylo-scope-nth-independent-v1/REPORT.md`;
  WPT baseline in `artifacts/stylo-scope-nth-fix-v1/`.
- Handwritten scope-cache contract and finite bug witnesses:
  `artifacts/stylo-scope-cache-proof-v1/README.md`. These proofs followed source/native
  discovery; they do not establish Rust or Gecko refinement.
- Implicit owner movement (no defect): `artifacts/stylo-implicit-scope-owner-v1/OWNER-MOVE-REPORT.md`;
  192 state comparisons with fresh DOMs agree. Shared/adopted/cloned sheet audit:
  `artifacts/stylo-implicit-scope-independent-v1/REPORT.md`.
- Accepted CSS scope-model checkpoint and source-only archive reproduction:
  [ROOT-CHECKPOINT-20261017.md](ROOT-CHECKPOINT-20261017.md). The independent
  research commit is not a production bugfix.

- Scope-limit relative invalidation: `artifacts/stylo-scope-limit-fix-v1/verification.json`;
  independent reduction and patched replay in
  `artifacts/stylo-scope-limit-invalidation-independent-v1/` and
  `artifacts/stylo-scope-limit-invalidation-patch-review-v1/`.

## Maintenance

Add a pending entry when a defect is confirmed. Replace it with the full hash
after the standalone fix and regression test are committed; record actual local
test outcomes and limitations. Refresh hashes after any history rewrite. Keep
new findings separate from already completed fixes, and never record a research
or tooling commit as a production bugfix.

- Filtered nth relative invalidation: `artifacts/stylo-filtered-nth-fix-v1/verification.json`; independent terminal review and replay in `artifacts/stylo-filtered-nth-relative-audit-v1/`.

- Scope-dependent nth sharing: `artifacts/stylo-scope-nth-sharing-fix-v1/verification.json`; bounded proof and independent replay in `artifacts/stylo-scope-nth-revalidation-proof-v1/`.

## Breadth audit follow-up

- Name-only container query invalidation: the final 12-case WPT covers name
  addition and removal, three container types, and document/shadow descendants.
  Baseline 12 failures become 12 passes; all 26 selected subtests pass after the
  one-line dependency fix. Six original state comparisons also pass. Build and
  source/spec review complete; committed as `238710ff9db7f54449c075bf80c7c3d40b43387a`. Evidence:
  `artifacts/css-container-name-fix-v1/verification.json`.
- Animation finite iteration identity/parity and true-infinity direction:
  independent expanded 44-case timing WPT has nine failures; eight event
  tests have three failures. Committed as `0a81e1f36ab08a6d67ddd0bdd590e4661ff9b0a1`; all 52 new cases pass. Consumer/FFI trace and spec oracles:
  `artifacts/css-animation-iteration-review-v1/REPORT.md`.
- Literal negative zero: a follow-up 12-case probe finds three mismatches with
  current CSS Values prose, which requires literal `-0` to be positive zero.
  Existing upstream `signed-zero.html` deliberately expects the opposite.
  CSSWG issue9750 contains a later editor statement supporting literal
  negative zero, consistent with existing WPT. This is a spec/test conflict,
  not an accepted new Gecko bug; parser behavior and Round commit stay unchanged.
  The arithmetic-generated negative-zero tests avoid either interpretation. Evidence: `artifacts/css-literal-zero-review-v1/REPORT.md`; original probe retained in
  `artifacts/css-literal-zero-investigation-v1/`. Existing signed-zero WPT
  passes all 162 subtests on the combined Round/container build.

- Animation iteration verification: `artifacts/css-animation-iteration-fix-v1/verification.json`.

- Animation bounded proof and independent replay: `artifacts/css-animation-iteration-proof-v1/ROOT-REVIEW-v2.json`; six audits, no native/IEEE/event refinement.

## Second breadth audit follow-up

Static reports and finite native confirmations are collected under
`artifacts/css-breadth-audit-round2-v1/`. The three new pending entries above
are not committed fixes or formal-verifier discoveries. They arose from static
spec/source audits and explicit browser probes. Actual process42002 and39481
both exited1 for the expected mismatches; binary/script inputs stayed unchanged.
`probes/RESULTS-v1.json` binds raw evidence. Generic runner exception text refers
to mutation/fresh parse, but these probes use explicit computed-value oracles.

- Shorthand-cache fix verification: `artifacts/css-shorthand-cache-fix-v1/verification.json`; independent terminal review and bounded8-law proof accepted.

## Third breadth audit follow-up

`artifacts/css-breadth-probes-round3-v1/RESULTS-v1.json` records actual terminal
sessions28562 and46879, each exit1 for semantic mismatches. All26cases parse;
browser, XUL, scripts and runner hashes remain unchanged. Math has12mismatches
across21cases, including2already-known pow failures. Transforms has6component
mismatches in2of5cases, with all3controls passing. These observations followed
static spec/source analysis; no Lean-discovery or release-prevalence claim is
made. Independent source/spec reviews are in `css-math-oracle-review-v1` and
`css-transform-deferred-review-v1` under artifacts. Known pow failures remain
calibration evidence rather than an additional newly discovered bug.

## Fourth breadth follow-up: reproduced candidates

No commits yet for these candidates. Independent normative acceptance is still
in progress; these are browser mismatches, not formal-verifier discoveries.

| Candidate | Commit | Evidence |
| --- | --- | --- |
| Numeric attr whitespace and whole-token fallback | pending signing | 22 FAIL / 31 PASS become 53 PASS; 247 existing passes unchanged; token-model proof and 2,450 bridge cases accepted; `artifacts/css-attr-numeric-fix-v1/verification.json` |
| Active attr fallback-cycle discovery | pending |16of32cases disagree, ordinary/valid-primary controls pass; same evidence |
| Equal-size physical/logical animation shorthand precedence | pending signing | 12 FAIL / 7 PASS become 19 PASS; 23 existing passes and two expected failures unchanged; isolated native/WPT patch and 14-audit conditional winner proof accepted; `artifacts/css-logical-shorthand-fix-v1/verification.json` |
| Early calc length conversion normalizes exceptional operands | pending review |Clamp-free width/opacity probes fail,2finite controls pass; `artifacts/css-calc-conversion-probes-v1/RESULTS-v1.json` |

Counter sentinel and reversed repeated-name candidates remain unexecuted static
hypotheses and are not counted as confirmed bugs.

Independent review accepts the two attr behaviors as separate conformance bugs:
`artifacts/css-breadth-audit-round4-v1/independent-attr-review/REVIEW.md`. Root
accepts equal-size animation conflict after checking the current ordered spec
rules and native comparator; receipt:
`artifacts/css-breadth-probes-round4-v1/ROOT-LOGICAL-REVIEW-v1.json`.
These acceptance decisions do not establish novelty or regression ranges.

## Fifth breadth follow-up: accepted observable bugs

Independent current-spec/native review accepts the following behavior families.
They were discovered by static comparison and browser probes, not by Lean.
Novelty and release-browser prevalence remain unestablished. Turkish dotted I
is existing bug 1887395 and is excluded from this list.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Abspos subgrid placement clamps nonexistent lines into valid endpoints | pending signing | Expanded WPT: 32 FAIL / 164 PASS become 196 PASS; 16 existing subtests and four reftests pass, one expected reftest failure unchanged; `artifacts/css-grid-abspos-fix-v1/verification.json`. |
| Greek sigma casing uses Letter/Mark instead of required Unicode context properties | pending signing | 67 FAIL / 44 PASS become 111 PASS, and the new fixed-font rendering test now passes; 105 masking and 287 existing password assertions plus 24 compatibility reftests unchanged; `artifacts/css-sigma-fix-v1/verification-final-v1.json`; independent source, browser and scoped proof review accepted. |
| Lithuanian casing loses context across combining marks and omits above-mark cases | pending | Four incorrect innerText results; context-scanner repair and paired rendering WPT pending. |
| Whitespace transformation changes across equivalent text-node/inline partitions | pending | Six geometry discrepancies with all control partitions passing; WPT and mapped-flow repair pending. |

Evidence: `artifacts/css-breadth-probes-round5-v1/RESULTS-v1.json`. Independent
acceptance and root authentication:
`artifacts/css-breadth-audit-round5-v1/independent-review/ROOT-ACCEPTANCE-v1.json`.
The corrected adjacency citation is CSS Text `#text-encoding`; historical
producer reports are preserved, with the correction recorded independently.

## Sixth breadth follow-up: accepted observable bugs

These were found through static spec/native comparison and browser probes.
Independent review accepts the bounded scenarios below; root authenticated
101 evidence identities before the sizing native edit. No novelty or release
prevalence claim is made. The ratio family already has expected WPT failures,
and broad fragmentation/aliasing issues have historical Bugzilla coverage.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Replaced Grid max-content inline size is overridden by initial stretch | pending signing | 24 FAIL / 24 PASS become 48 PASS; three existing reftests and four expected WPT042 failures unchanged; initial-selection proof and isolated native/WPT patch accepted; `artifacts/css-sizing-stretch-fix-v1/verification.json`. |
| Replaced border-box aspect ratio loses box adjustment under min/max constraints | pending | Canvas height 55.550003 instead of 50; three controls pass; existing WPT042 four expected failures reproduced. |
| Page-only requests affect fieldset/Grid placement in screen columns | pending | Four fieldset and eight Grid scenarios disagree with auto; ordinary-block page-only and nine incremental/fresh controls pass. |
| Ordinary block ignores modern break-before:always in columns | pending native investigation | Separate positive control stays at (0,20) instead of next column (100,0); not folded into page-only filtering repair. |

Evidence: `artifacts/css-breadth-probes-round6-v1/RESULTS-v1.json` and
`artifacts/css-breadth-audit-round6-v1/independent-review/ROOT-ACCEPTANCE-v1.json`.


## Seventh breadth follow-up: accepted observable bugs

The independent conditions review accepts six bounded defect families after
recomputing the probe oracles and authenticating sources, inputs and results.
Root read the review and authenticated its six retained files. These findings
come from static analysis and browser probes, not from Lean discovery. Novelty,
regression ranges and release-browser prevalence have not been established.

| Finding | Commit | Regression evidence / next gate |
| --- | --- | --- |
| Outer container-query operators omit attribute dependencies | pending signing | 76 FAIL / 8 PASS become 84 PASS; all 139 existing subtests unchanged. Independent native/WPT and scoped proof reviews accepted; `artifacts/css-query-attribute-wrappers-fix-v1/verification-final-v1.json`. |
| Constant border-box dimensions conceal changed query content dimensions | pending signing | 72 FAIL / 72 PASS become 144 PASS; 92 controls pass with the same four existing unexpected passes. Independent native/WPT and scoped proof reviews accepted; `artifacts/css-query-content-box-fix-v1/verification-final-v1.json`. |
| Deferred size query selects an ineligible nearer ancestor | pending | Two intervening-ancestor cases fail in both reused and fresh documents; direct/literal/named/eligible-inner controls pass. |
| Deferred query threshold changes do not invalidate the result | pending | Named and unnamed threshold mutations remain stale at fixed size; fresh results are correct. |
| Registered boolean style queries test presence instead of initial-value equality | pending | Three initial/default-value cases incorrectly match; noninitial and explicit-initial controls pass. |
| Style queries treat unset as absence instead of resolving the property's default | pending | Four inherited/registered cases incorrectly fail; differing-value controls pass. |

Evidence: `artifacts/css-breadth-probes-round7-v1/conditions/RESULTS-v1.md` and
`artifacts/css-breadth-audit-round7-v1/conditions-independent/REPORT.md`.
Root authentication: `artifacts/css-query-attribute-wrappers-fix-v1/ROOT-REVIEW-PINS-v1.json`.
Four unknown-feature OR failures are existing WPT expectations, not new entries.
Each family retains a separate prospective fix/WPT commit. No commit hash exists
for these entries yet; signing remains blocked and has not been disabled.


### Seventh breadth rendering and timing follow-up

| Finding | Commit | Evidence / qualification |
| --- | --- | --- |
| Displaced gradient hints discard linear-sRGB interpolation while materializing stops | pending compositor gate and repair | Six software snapshot samples are 128 instead of approximately 188; 34 controls pass. `artifacts/css-breadth-probes-round7-v1/runtime-independent/REVIEW.md`. No compositor/release output claim. |

Large-step extrapolation is a confirmed observable consequence of the known
bug 1706157 fallback, retained as a scoped repair candidate rather than a novel
overflow discovery. Distinct keyframe offset collapse is observed precision loss
with unresolved conformance; it is not an accepted conformance-bug entry.


## Eighth breadth follow-up: accepted scroll-snap defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Off-axis oversized snap area admits an invalid resting position | pending | Both x/y stop at 400 despite the only valid position being 0; removal, small-area and semantic controls pass. |
| Zero-area snap target loses retention after consecutive layout changes | pending | Both x/y, with and without competitor, follow 500→550 then remain at550 when target moves to800; nonzero-area and single-jump controls pass. |

Root normative/source/raw geometry review:
`artifacts/css-breadth-probes-round8-v1/scroll-snap/ROOT-REVIEW-v1.md`.
The fixture author's separate receipt recalculation is explicitly disclosed.
The completed run has 24 cases/44 states, six differences in64 correctness
comparisons, and840 passing geometry comparisons; all support/setup/settling
checks pass. No release, regression-range or novelty claim. Each family needs
its own native/WPT repair and preceding proof/tooling companion.

## Eighth breadth follow-up: accepted table sizing defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Negative spanning-cell contribution removes required table border spacing | pending signing | 30 FAIL / 60 PASS become 90 PASS; 61 existing passes and 11 expected failures unchanged. Native/WPT and scoped proof reviews accepted; `artifacts/css-table-span-spacing-fix-v1/verification-final-v1.json`. |
| Unassigned fixed-layout columns discard the allocation remainder | pending | 18 states yield a 101px table, 100px track sum and 1px end gap instead of zero; explicit-zero and divisible controls fill. |

Independent review: `artifacts/css-breadth-probes-round8-v1/tables-independent/REPORT.md`.
Root acceptance: `artifacts/css-breadth-probes-round8-v1/tables/ROOT-REVIEW-v1.json`.
Both fresh and mutated documents show the same failures; 15,558 consistency
checks agree. These are two sizing families, not 102 distinct bugs. WPT baseline
settings include disabled pixel alignment and must be tested separately. The
residual tolerance is a Gecko diagnostic criterion, not universal CSS precision.
Each fix needs a separate native/WPT commit and preceding proof companion.

## Ninth breadth follow-up: accepted polygon defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Large polygon coordinates corrupt float exclusion before margin-box clipping | pending signing | 16 FAIL / 16 PASS become 32 PASS; two existing clipping reftests unchanged. Native/WPT and bounded arithmetic proof accepted; `artifacts/css-polygon-intercept-fix-v1/verification-final-v1.json`. |

Independent acceptance: `artifacts/css-breadth-probes-round9-v1/polygon-independent/REVIEW.md`.
Root evidence: `artifacts/css-breadth-probes-round9-v1/polygon/ROOT-REVIEW-v1.json`.
The native signed product exceeds its range even when the correct intercept is
small. Browser evidence is not an instrumented UB trace. No release, novelty or
security-impact claim. The widened helper preserves anchored integer rounding;
15 Lean audits and 29,615 native cases pass under explicit bounded-difference
and defined-preprocessing premises. The standalone patch contains only native
source and WPT; its 17-file proof companion is separate. Signing remains pending.

## Ninth breadth follow-up: accepted transform geometry defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| CSS-layout stroke-box leaves reference dimensions empty | pending signing | 72 FAIL / 144 PASS become 216 PASS; four CSS/SVG reftests unchanged. Native/WPT and scoped alias/cache proof accepted; `artifacts/css-stroke-reference-box-fix-v1/verification-final-v1.json`. |
| Perspective origin omits the reference-box displacement | pending | 12 states fail; padded content-box origins project child positions using the wrong center. Equivalent border-box, zero-padding and zero-Z controls pass. |
| Overflow clip incorrectly forces preserve-3d flattening | pending rendering gate and repair | 12 states give 25px instead of 100px along the rotated axis. Visible, hidden, flat, opacity and paint-containment controls pass; compositor/clipping not verified. |

Independent acceptance: `artifacts/css-breadth-probes-round9-v1/transforms-independent/REPORT.md`.
Root authentication: `artifacts/css-breadth-probes-round9-v1/transforms-geometry/ROOT-REVIEW-v1.json`.
All 47 semantic-control states pass. All 324 fresh/mutated component comparisons
agree. These are three geometry families, not 56 distinct bugs. Each needs its
own native/WPT commit and preceding companion. No release or novelty claim.

## Ninth breadth follow-up: accepted partial image sizing defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Missing intrinsic ratio discards an available natural dimension under object-fit none/scale-down | pending signing | Two new reftests improve FAIL→PASS; six existing SVG controls unchanged. Native/WPT and scoped proof accepted; `artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json`. |

Evidence: `artifacts/css-breadth-probes-round9-v1/object-fit/ROOT-REVIEW-v3.json`
and `artifacts/css-breadth-probes-round9-v1/object-fit-independent/REPORT.md`.
All V3 source-loading, support, geometry and literal-reference gates pass.
V1 failed before measurement; V2 remains unqualified because two source metadata
observations were stale. Those attempts are preserved. The missing-ratio shortcut
has prior code history; no novelty, release-browser or compositor claim is made.
Next is a separate native/WPT repair and preceding optional-dimension proof.

## Tenth breadth follow-up: accepted positioning defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Fixed-margin excess is lost before absolute auto-margin resolution | pending signing | Expanded WPT: 240 FAIL / 552 PASS become 792 PASS; 70 existing subtests, two reftests and eight expected failures unchanged. Native/WPT and scoped proof accepted; `artifacts/css-abspos-auto-margin-fix-v1/verification-final-v1.json`. |
| Explicit-inset self-alignment uses a differently oriented static wrapper’s coordinates | pending | 24 displaced-position states per active/fresh mode; actual-CB alignment controls pass. Native/WPT repair and coordinate provenance proof pending. |

Independent report: artifacts/css-breadth-probes-round10-v1/positioning-independent/REPORT.md.
Root checker replay exits 0 and matches the independent receipt byte-for-byte;
root acceptance: artifacts/css-breadth-probes-round10-v1/positioning/ROOT-REVIEW-v1.json.
All 70 semantic-control states and 1,440 calibration components per mode pass;
all 600 active/fresh components agree. Two defect families, not 74 bugs.
The initial acceptance excluded negative IMCBs. Later primary issue review found
the CSSWG zero-floor resolution and reaffirmation; the expanded repair tests
negative IMCBs separately from negative post-margin space. See
artifacts/css-abspos-auto-margin-fix-v1/DESIGN-v1.md. No invalidation, novelty, or release claim.
Each family requires its own native/WPT commit with a preceding proof companion.

### Object-fit partial natural dimensions repair accepted

Native/WPT repair and scoped proof reviews are complete; commits are pending
configured signing. Both new reftests improve from FAIL (48,000 pixels each) to
PASS; all six existing SVG controls remain PASS. Fifteen Lean audits and 2,355
extracted-helper cases pass producer/root/independent replays with identical
receipts. ScaleDown whole-candidate selection is proved only for at most one
natural dimension; two both-present/no-ratio boundary changes are explicitly
excluded. Positive-ratio dispatch is preserved, not newly proved geometrically.
The standalone patch contains native source plus four WPT files; its 15-file
tooling companion precedes it. Final evidence:
artifacts/css-object-fit-partial-fix-v1/verification-final-v1.json.

## Eleventh breadth follow-up: accepted block-flow discrepancy

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Endpoint zero tests allow positive size or padding to collapse through | pending signing | New WPT: 36 FAIL / 54 PASS become 90 PASS; five existing reftests unchanged. V2 boundary probes pass: ten wrong offsets become zero; fragmented expression/literal geometry agrees, with no literal-control changes. |

Independent review: artifacts/css-breadth-probes-round11-v1/block-flow-independent/REPORT.md.
Root replay exits 0 with identical checker bytes and 146 authenticated review files;
acceptance: artifacts/css-breadth-probes-round11-v1/block-flow/ROOT-REVIEW-v1.json.
Positive preferred-height and bottom-padding paths are one candidate collapse
classification repair family. All raw active/fresh rectangles and styles agree;
this is not an invalidation finding. Repair design must preserve zero/unknown
eligibility and consider resolved sizes, padding, min/max sizing and fragmentation.
No release, novelty or universal used-zero/computed-zero equivalence claim.
The fix needs a standalone native/WPT commit with a preceding proof companion.

## Eleventh breadth follow-up: accepted masking defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Empty explicit SVG mask region skips required subtract/intersect composition | pending signing | Two new 80-cell static/mutation reftests improve FAIL→PASS; four existing reftests unchanged. Zero width/height and alpha/luminance covered; explicit empty-region output preserves other null causes. `artifacts/css-svg-empty-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json`; three-layer partial-alpha/transform/clip reference also passes. |
| Prepared CSS mask image with empty fill skips required subtract/intersect composition | pending signing | Four new reftests improve FAIL to PASS; four existing reftests unchanged. Covers zero dimensions and images positioned outside the painting area. Ten-line native repair and standalone WPT, plus passing rounded-clip boundary; `artifacts/css-image-zero-mask-fix-v1/ROOT-NATIVE-REVIEW-v1.json`. |

Independent review: artifacts/css-breadth-probes-round11-v1/masking-independent/REPORT.md.
Root replay 27773 exits 0 and matches the independent checker byte for byte;
438 review files authenticate. All 208 PNGs were independently decoded through
ImageIO, with eight wrong states/80,000 pixels per mode, 96 passing semantic
controls per mode, and no retained/fresh differences. Root acceptance:
artifacts/css-breadth-probes-round11-v1/masking/ROOT-REVIEW-v1.json.
These are two independently repairable native sites under one alpha-composition
contract; each needs its own native/WPT commit and preceding companion. Evidence
is software drawSnapshot only, with no compositor, release or novelty claim.

## Twelfth breadth follow-up: accepted duplicate adoption defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Last-occurrence sheet filtering discards earlier named-layer introductions | design reviewed; prototype/standards gates pending | 48 wrong named-layer colors per active/fresh mode across Document and ShadowRoot; all 180 semantic-control states per mode pass. |

Independent report: css-breadth-probes-round12-v1/cssom-duplicates-independent/REPORT.md.
Root replay matches the independent receipt byte for byte, with 174 frozen files
authenticated. Root acceptance: css-breadth-probes-round12-v1/cssom-duplicates/ROOT-REVIEW-v1.json.
This is one ordering family, not an invalidation-only defect or one bug per state.
The 12 anonymous-important differences per mode remain exploratory. A repair
must preserve both first layer introductions and last declaration precedence;
changing to first-only filtering or passing duplicates into unique storage is
insufficient. Native/WPT repair and preceding formal companion remain pending.

## Thirteenth breadth follow-up: accepted bad-URL recovery defect

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Whitespace-to-bad-URL handoff consumes a backslash before escape-aware recovery | pending signing | New WPT: 28 FAIL / 36 PASS become 64 PASS; five adjacent passes and three expected failures unchanged. |

Independent report: css-bad-url-recovery-independent-v1/REPORT.md. Root replay
matches its paired checker byte for byte, with 87 review files authenticated.
Root acceptance: css-bad-url-recovery-fix-v1/ROOT-NATIVE-REVIEW-v1.json.
The standalone patch contains only the tokenizer, required vendor checksum, and
WPT and applies to original base and HEAD. Initial builds that reused the cached
vendored crate are preserved; acceptance uses confirmed recompilation/relink and
paired WPT run 79528. The scalar suffix proof and finite exact native capsule
have passed root and independent review; see final acceptance below.
This was found by static spec/source analysis, then reproduced in the browser;
no Lean discovery, release impact, novelty or security claim is made.

### Block-flow collapse repair fully accepted

Native/WPT and scoped formal reviews are complete. Producer 9753, root 22432
and independent 78776 exit 0 with identical receipts: 34 Lean audits, 2,180 native
fixtures and 2,532 model evaluations. Independent stack-machine reconstruction
matches all 4,360 original/candidate outputs and all model outputs. Root replay
of the review verifier authenticates 156 frozen files. The universal model covers
finite normal-line trees with supplied providers; arbitrary fragmentation and
provider correctness remain outside it. A 25-file source/tooling companion must
precede the two-file native/WPT commit. Final acceptance:
artifacts/css-block-flow-collapse-fix-v1/verification-final-v1.json.

### Bad-URL recovery repair fully accepted

Native/WPT and scoped formal gates are complete. Producer 18271, root 24730
and independent 61915 exit 0 with identical receipts: 25 Lean audits, 7,132 native
fixtures in each macro mode and 8,268 model evaluations. The independent oracle
checks 85,584 candidate fields and 33,072 model suffix fields; root replay of the
review verifier authenticates 428 frozen files. The universal scalar theorem
does not prove raw UTF-8/native-state correspondence. A 229-file source/tooling
companion precedes the three-file tokenizer/checksum/WPT fix. Final acceptance:
artifacts/css-bad-url-recovery-fix-v1/verification-final-v1.json.

## Fourteenth breadth follow-up: accepted nesting specificity defects

| Finding | Commit | Evidence / next gate |
| --- | --- | --- |
| Packed specificity delta borrows across components during nesting substitution | pending signing | 22 failing WPT subtests become PASS; all38new,11existing subtests and3reftests pass. Optimized native/performance and scoped formal reviews accepted; verification-final-v1.json in css-nesting-specificity-fix-v1. |
| Invalid nesting parent arm retains ID/class prefix specificity | pending repair | Two browser discrepancies; plain parent substitution independently exhibits the error. Whole-arm filtering must preserve inner forgiving boundaries. |

Five shared controls pass. Root read the independent report and checker, replayed
it with exit 0 and authenticated 20 retained files and 36 stable runtime pins.
These are two separate reproduced defect families, requiring separate native/WPT
commits. They were found by source inspection and browser probes, not Lean.
Expanded controls and mutation/fresh equivalence remain required before repair
acceptance. Evidence: css-breadth-probes-round14-v1/ROOT-NESTING-REVIEW-v1.json.

## SVG formal acceptance and round 15 browser lead

SVG native/WPT and corrected v2 formal companion are accepted. Final packaging:
`artifacts/css-svg-empty-mask-fix-v1/verification-final-v1.json`. This is the
twentieth fully accepted repair awaiting configured signing. The v1 native
capsule remains rejected historical evidence.

The round15 bidi image probe reproduced four ordering discrepancies with eight
passing controls and 49 stable input pins. Independent defect review is pending;
no native patch or formal acceptance is claimed. Evidence:
`artifacts/css-breadth-probes-round15-v1/bidi-baseline-v1/ROOT-RESULTS-v1.json`.

## Fifteenth breadth follow-up: browser discrepancies under review

| Family | Commit | Gate |
| --- | --- | --- |
| Inline image embed/override loses specified strong bidi direction | pending repair | Four failures and eight controls pass; loaded images and both paragraph directions. |
| Collapsed spanning ruby annotation retains width | pending repair | Fresh/mutated collapse fails across three writing modes; explicit collapse and visible/hidden controls pass. |
| Sole preserved ruby whitespace is removed | pending repair | Direct, split-run and rbc cases fail across three writing modes with computed pre; explicit rb references pass. |
| Scrolling element style change misses anchor suppression | pending repair | Margin plus growth reaches 130 instead of 100; six controls pass. |
| Transformed fixed child can be selected as scroll anchor | native/WPT pass; independent review and proof pending | New WPT repairs one failure and preserves four controls; three existing tests pass. Original thirteen-case probe changes only the intended fixed-child case. |

These are not fixed or formally accepted yet. Root evidence:
`artifacts/css-breadth-probes-round15-v1/REPORT-v1.md`. Independent reviews are
assigned; retain separate repair/WPT commits if accepted.

Bidi independent defect review is now root-accepted:
`artifacts/css-breadth-probes-round15-v1/ROOT-BIDI-REVIEW-v1.json`. The other
round15 families remain under independent review. No patch acceptance is implied.

Ruby independent defect review is root-accepted for two separate inline-geometry
repairs: `artifacts/css-breadth-probes-round15-v1/ROOT-RUBY-REVIEW-v1.json`.
The trim-only repair is explicitly unsafe because later whitespace interpretation
assumes nonboundary neighbors. No production fix is accepted yet.

## CSS image final acceptance; nesting performance correction

The CSS image empty-fill repair is fully accepted within native/WPT and scoped
formal boundaries: `artifacts/css-image-zero-mask-fix-v1/verification-final-v1.json`.
The preceding source-only companion uses `tooling-paths-v2.txt` and
`SOURCE-PACKAGE-v2.md`; historical full-artifact verification is separate.
This is the twenty-first fully accepted repair awaiting configured signing.

Nesting A's first native candidate fixes all 22 failing WPT subtests; all 38 new
subtests and existing 11 subtests/3 reftests pass. Expanded boundary tests preserve
four separate B failures. However, actual-crate benchmarks show a material
35.06x slowdown at 1,000 parent arms/100 ampersands. This candidate is not accepted
for landing. A cached direct-parent contribution revision is under development.
Evidence: `artifacts/css-nesting-specificity-fix-v1/ROOT-WPT-REVIEW-v1.json` and
`artifacts/css-nesting-specificity-proof-v1/PERFORMANCE-REVIEW-v1.json`.

Both scroll anchoring defects are now independently reviewed and root-accepted
for separate repairs: `artifacts/css-breadth-probes-round15-v1/ROOT-SCROLL-REVIEW-v1.json`.
All five round15 findings have passed defect review; no round15 native patch
is accepted yet.

### Optimized nesting repair passes rebuilt browser gates

V2 caches direct-parent contributions and freshly counts other substituted
components. Root and independent source/performance reviews accept this strategy;
small overhead remains possible. Build26044 and WPT86724 exit0: all38new subtests,
11existing subtests and3reftests pass. Boundary87668 exits0 with all88observations
matching the earlier correctness-passing candidate, including four unchanged
separate B failures. The three-file patch applies independently at original base
and HEAD. Formal companion and final independent native binding remain pending.
Evidence: css-nesting-specificity-fix-v1/ROOT-WPT-REVIEW-v2.json,
ROOT-BOUNDARY-REVIEW-v2.json and ROOT-PERFORMANCE-GATE-v2.json.

The new fixed-scroll-anchor WPT baseline94273 reproduces one expected failure
and passes four semantic controls plus three existing tests. The isolated native
exclusion is applied, but not yet built or accepted. Evidence:
css-scroll-fixed-anchor-fix-v1/ROOT-BASELINE-REVIEW-v1.json.

### Nesting proof replay and fixed-anchor candidate

Optimized nesting native/WPT is independently accepted and root-reviewed in
css-nesting-specificity-fix-v1/ROOT-NATIVE-REVIEW-v2.json. Producer87069 and root91589
formal/native replays exit0 with identical receipt7863647d:29Lean theorems,133typed
comparisons,145actual-crate cases per variant,10native and6Lean semantic mutants.
Independent formal review remains required; no universal Rust refinement is
claimed. Source-only companion packaging is being clarified before acceptance.

Fixed-anchor build17708 and paired41566 exit0:all5new subtests and3existing tests
pass. Boundary25742 exits0 with159stablepins:all13case objects match original
except the repaired fixed-transformed case. The separate scroller-margin failure
remains;11controls pass. Format76021 exits0 with12unrelated restorations;lint12686
exits1 with0errors/1ignored-WPTwarning. The two-file patch applies at original
base and HEAD. Independent native/WPT review and a complete classifier/traversal
proof companion remain pending. Evidence:css-scroll-fixed-anchor-fix-v1/ROOT-WPT-REVIEW-v1.json
and ROOT-BOUNDARY-REVIEW-v1.json.

### Round16 lead, pending independent defect review

Zero-area motion-path reference geometry is reproduced in local run54822:
18polygon candidate cases fail,54controls pass,99inputs stable,all288observations
checked against an independent coordinate oracle. Fresh/mutated results agree.
This is a preliminary discrepancy, not an accepted new bug or native fix.
Evidence:css-breadth-probes-round16-v1/ROOT-MOTION-RESULTS-v1.json.

Configured signing retry36232 again exits128 with the 1Password buffer error.
HEAD and the12staged proof files remain unchanged; no local commit was created.

### Optimized nesting repair fully accepted

Final native/WPT/performance and scoped formal acceptance:
`artifacts/css-nesting-specificity-fix-v1/verification-final-v1.json`.
The standalone fix contains parser.rs,builder.rs and its WPT;43source/tooling/
guidance files precede it. Producer,root and independent replay receipts match.
The29producer theorems and one independent packed-order supplement have distinct
scopes; finite actual-crate execution is not universal Rust refinement. Invalid
parent-prefix defectB remains separate. This is the twenty-second fully accepted
repair awaiting signing; no new commit hash exists yet.

## Round16 motion defect accepted; generated-grid and text-overflow gates

| Finding | Commit | Current gate |
| --- | --- | --- |
| Valid literal polygon is discarded for a zero-area motion-path reference | pending repair | Independent normative/native review accepted; 18 failing cases and 54 passing controls, 288 observations |
| Whitespace-only generated grid content creates an anonymous row | pending repair | 12 failing cases, 36 passing controls; 192 observations |
| Text-overflow effective marker width leaks between lines | pending repair | 400 wrong pixels per capture; related controls pass |
| Vertical text-overflow marker paints into inline-end padding | pending repair | Both vertical modes show 400 wrong pixels per capture |
| Clip-to-marker mutation lacks cached float line edges | pending repair | 1,600 wrong pixels before and after separate control reflow; fresh/reflowed controls pass |

Root runtime records and motion acceptance live in
`artifacts/css-breadth-probes-round16-v1/`. Text-overflow strict pixel run59089
is rejected; versioned run22747 passes font/reference/control gates with an
explicit bounded glyph-edge mixture rule. These are source/browser findings,
not bugs discovered by Lean. No native repair is accepted from these probes.

Fixed-anchor independent native/WPT review now passes root replay:
`css-scroll-fixed-anchor-fix-v1/ROOT-NATIVE-INDEPENDENT-REVIEW-v1.json`.
Its scoped formal companion remains pending, so the fully accepted repair
count remains 22 awaiting configured signing.

### Round16 independent defect reviews complete

All five round16 families are accepted for separate repairs. Generated-grid
review/root replay authenticates 73 files and all 192 observations. Text-overflow
review/root replay13525 exits0, authenticating 204 files/180 origins, all three
retained PNGs and 78 crops (including the rejected strict run). Independent
source/spec, font and rational pixel oracles support all three families.
Accepted review records are ROOT-*-INDEPENDENT-REVIEW-v1.json under
css-breadth-probes-round16-v1; synthesis is css-breadth-audit-round16-v1/REPORT-v2.md.

Fixed-anchor producer67512 and root69253 full formal replays exit0 with identical
summary00fb866e: 4,929 native cases per variant and Lean exports, 48 audited
theorems, 12 complete native semantic mutants, six executable Lean mutation
witnesses and eight separate diagnostics. Independent formal review remains
pending; no change to the count of 22 fully accepted repairs awaiting signing.


### Text-overflow line-state repair: paired browser gates passed

Commit remains pending. The isolated fix is two assignments in TextOverflow.cpp
plus four WPT reftests and one shared reference. Static/growth/restoration change
FAIL→PASS; shrink and ten existing outcomes are unchanged. Six-file patch applies
at originalbase+HEAD: css-text-overflow-line-state-fix-v1/fix-candidate-v1.patch.
Formal companion and independent native acceptance remain pending. The separate
rectangle probe retains one corner-pixel rejection; do not report it as a full
pixel-oracle pass. Evidence: ROOT-WPT-REVIEW-v1.json and ROOT-BOUNDARY-REVIEW-v1.json.

Fixed-anchor formal v1 is partial against its original scope. Independent raw-list
Lean traversal and rich-trace agreement are required in v2 before final acceptance;
its native/WPT review remains accepted. No new fully accepted repair is counted.

Round17 font matching has two reproduced preliminary families, awaiting independent
defect review: fractional scalar-score priority inversion and oblique search
threshold. Sixteen candidate cases reproduce, twelve controls pass. No fix commit
exists; css-breadth-probes-round17-v1/ROOT-FONT-RESULTS-v1.json records the gate.

Signing retry41015 exits128 (1Password buffer error); original HEAD and twelve
staged companion files remain unchanged. Twenty-two fully accepted repairs still
await signing. No unsigned commits or pushes were made.


### Round18 checkpoint: formal gates and preliminary breadth leads

Text-overflow A now has accepted independent native/WPT review and an exact
same-glyph boundary reference in both phases. The older rectangle oracle retains
its recorded one-pixel rejection. Root formal replay2756 passes and matches the
producer:20 theorem audits,138 cases,776 native rows per variant, seven native
semantic mutants and four executed Lean counterexamples. Independent formal
review is pending. Records: css-text-overflow-line-state-fix-v1/
ROOT-NATIVE-INPUT-CLOSURE-v2.json, ROOT-GLYPH-BOUNDARY-REVIEW-v2.json and
ROOT-FORMAL-REPLAY-v1.json. No final acceptance or new commit is claimed.

Fixed-anchor v2 root replay23530 passes with48 inherited plus37 new theorem
audits. Its4170 classifier rows and766 traversal rows are distinct coverage;
only the latter exercise independent traversal implementations. Source-only
closure verifies; independent formal review remains pending. Record:
css-scroll-fixed-anchor-fix-v1/ROOT-FORMAL-REPLAY-v2.json.

Round18 whitespace runtime retains two unexpected ASCII partition-control
failures; the overall run is not a pass. Zero-tab intrinsic sizing and positive
tabs at zero font size are reproduced leads awaiting independent adjudication.
Tiny-tab advance policy remains unresolved, and partition extensions overlap an
existing family. No new accepted bug is added. Record:
css-breadth-probes-round18-v1/ROOT-WHITESPACE-RESULTS-v1.json.

Counts remain16 committed fixes and22 fully accepted repairs awaiting signing.


### Fixed-anchor repair fully accepted

Independent v2 formal replay91017 and root checker both pass, matching producer
and root full replay summary0471241f. Root read the complete independent report,
raw-wire oracle and verifiers. The required independent interpreter milestone is
satisfied:37 new and48 inherited theorem audits,766 traversal graphs and4170
separate classifier inputs, with complete semantic trace comparison. Frame
construction, geometry, ownership and stable provider assumptions remain explicit;
this is not universal C++ refinement.

Final acceptance: css-scroll-fixed-anchor-fix-v1/verification-final-v2.json.
The39-file source-only companion precedes the standalone two-file native/WPT
patch. All current patch bytes still match the paired browser inputs. This is
the twenty-third fully accepted repair awaiting configured signing; no new
commit hash exists. Text-overflow formal independent review is now active.


### Text-overflow ordinary line-state repair fully accepted

Independent formal replay47771, root2756 and a fresh source-only replay16102 all
exit0 with identical receipt f2af5871. Root read and replayed the independent
raw-input oracle and verifier. The20 theorem audits and bounded native/model
comparison are accepted within the explicitly limited entry/cache scope; the
finite sequence theorem is definitional normalization, not C++ refinement.

Final acceptance: css-text-overflow-line-state-fix-v1/verification-final-v1.json.
The21-file source-only companion precedes the six-file native/WPT patch. This is
the twenty-fourth fully accepted repair pending configured signing. The original
rectangle residual remains documented alongside exact same-glyph references.

Round18 timeline run12247 reproduces two logical-axis errors on an orthogonal
pseudo scroller, with all six controls passing and39 stable inputs. Independent
review is queued after the anchor scout. Zero-tab WPT baseline56364 has126 FAIL
and18 PASS across144 subtests; thirteen existing reftests pass and one expected
failure remains. The zero-tab candidate is not yet applied. Independent tab
review is active. Signing retry86680 fails with the same1Password buffer error;
HEAD and twelve staged companion files are unchanged.


## Accepted defect queue and current repairs — 18 October 2026

| Finding | Commit | Evidence and remaining gates |
| --- | --- | --- |
| Zero-sized tabs inflate intrinsic inline size | accepted; signing pending | 126 failures become passes; all 144 new WPT cases pass. Native/WPT and corrected formal v2 independent reviews accepted and root replay passes. Final evidence: css-tab-zero-intrinsic-fix-v1/verification-final-v1.json. Preceding 33-file tooling commit; standalone two-file Gecko/WPT commit. |
| Positive tabs at zero font size fail to advance at an exact stop | pending repair | Independent defect/design review accepted; separate patch/WPT/formal gates still required. |
| Fractional font scores violate width/style/weight priority | accepted; signing pending | All26new WPT pass,12baseline failures repaired independently of font threshold B. Full scoped proof, independent review, four-way browser matrix and final build/lint pass. Preceding96-path source companion; separate6-file repair. Final record: css-font-priority-fix-v1/verification-final-v2.json. |
| Oblique font search uses 14 degrees instead of the 11-degree threshold | accepted; signing pending | All38new WPT pass;18baseline failures repaired; existing outcomes unchanged. Scoped proof and independent formal/native/WPT review accepted. Default oblique remains14. Preceding62-file source companion; separate2-file repair. Final record: css-font-threshold-fix-v1/verification-final-v1.json. |
| Pseudo scroll timelines resolve logical axes using their host's writing mode | accepted; signing pending | Final40-case WPT passes,16baseline failures repaired; full scoped proof and independent review accepted. Preceding42-path source companion; separate3-file repair. Final record: css-timeline-pseudo-axis-fix-v1/verification-final-v1.json. Four recreation-opacity failures retained separately. |

Root acceptance records: `css-tab-zero-intrinsic-fix-v1/ROOT-NATIVE-INDEPENDENT-v1.json`,
`css-tab-zero-intrinsic-fix-v1/ROOT-BOUNDARY-REVIEW-v1.json`,
`css-tab-boundary-independent-v1/REPORT.md`,
`css-breadth-probes-round17-v1/ROOT-FONT-INDEPENDENT-REVIEW-v1.json`,
`css-breadth-probes-round17-v1/ROOT-FONT-DESIGN-v1.json`, and
`css-breadth-probes-round18-v1/ROOT-TIMELINE-INDEPENDENT-v1.json`.

The timeline baseline preserves an existing vertical view-timeline failure.
Recreation-opacity and anchor changed-phase discrepancies remain unaccepted
separate leads. Counts remain 16 committed fixes and 24 fully accepted repairs
pending configured signing; no new commit hash is claimed.


### Pseudo-timeline isolated repair gate

Exact final40case pair:16FAIL→PASS, all40newPASS,24existing subtestPASS,
1existing expectedFAIL and1reftestPASS unchanged. Native original/candidate
builds and final candidate WPT succeed in cycle78913. Three-file patch:
`css-timeline-pseudo-axis-fix-v1/fix-candidate-v2.patch`; exact application at
original base and HEAD is recorded in `standalone-apply-v2.json`.
Root evidence: `ROOT-WPT-REVIEW-v2.json`. Orthogonal-root controls, independent
native review and formal acceptance remain pending; this is not repair25 yet.
Four separate recreation-opacity failures are preserved in the full diagnostic.

Round19 scrollIntoView center probe reproduces8discrepancies with14controls.
Independent review must establish the normative oracle and relationship to
known clipping bug2036965 before accepting a new defect. Filter component-transfer
hypothesis remains static-only. Neither is counted as an accepted repair.
Signing retry46762 failed; no additional commit hash exists.


### Round20 verification checkpoint

Timeline root paired cycle31715 passes:128time observations in eightfixtures are
identical original/candidate. Final independent native/WPT review and root live
replay pass (319closed origins,42live); ROOT-NATIVE-INDEPENDENT-v1.json records
acceptance within that scope. Formal completion/review remains required.

Zero-tab formal v1 was rejected against four explicit scope/integrity gates.
Corrected v2 preparation23824 and source-only56319 pass with identical summary
2176ea22:35theorems,2931native cases per variant,12native and6Lean semantic mutants.
New coverage includes432negative intrinsic and120saturation cases. Independent
v2 review is active. This is not final repair acceptance.

Zoom probe26576 reproduces six inherited-lh and two root-rlh discrepancies, with
41passing controls and42stable inputs. These are preliminary findings pending
independent adjudication; inheritance overlaps bug1887627, and root rlh extends
the earlier round2 lead. ROOT-ZOOM-RESULTS-v1.json retains the limits.

Signing retry78531 exits128 with the same1Password buffer error. HEAD, index
tree and all12staged companion file hashes are unchanged. Counts remain
16committed fixes and24fully accepted repairs pending configured signing.

### Zero-tab intrinsic sizing repair fully accepted

The frozen v2 independent review accepts all four corrections. Root authenticated
758 review files, read its report, both independent oracles, applicability witness
and verifier, and replayed its live integrity/oracle gate successfully. Independent
full source-only replay5887 matches producer23824 and root56319, summary2176ea22.
The formal boundary remains explicit: model agreement and bounded native execution,
with saturation outside the unsaturated Lean bridge; no universal C++/IEEE proof.

Final acceptance: css-tab-zero-intrinsic-fix-v1/verification-final-v1.json.
The current native/WPT bytes match the accepted pair. A supplemental source-commit
guide uses --source-only for packaged verification; that invocation passes on the
isolated 32-file package. The guide makes the preceding tooling commit33files;
the following repair commit contains only nsTextFrame.cpp and its WPT.

Counts are16committed fixes and25fully accepted repairs awaiting configured
signing. No new commit hash exists. Positive tabs at zero font size remain separate.

### Font B paired repair; failed marker image preliminary finding

Final font B cycle40521 exits0 with both builds successful and all38new WPT
subtests passing, improving18baseline failures. Six existing reftests and four
parser subtests pass; three existing expected failures remain. Lint has0errors
and one ignored-file warning. The final two-file patch applies at original base
and HEAD; independent formal/native/WPT review remains required before acceptance.
Record: css-font-threshold-fix-v1/ROOT-WPT-REVIEW-v3.json.

Marker runtime25533 reproduces five empty-item40px-vs0observations with32controls,
including settled removal/restoration and fresh-clone comparison. This remains
a preliminary lead pending independent adjudication, with no repair or commit.
Record: css-breadth-probes-round21-v1/ROOT-MARKER-RESULTS-v1.json.
Sixteen committed fixes and25fully accepted pending repairs remain authoritative.


### Current acceptance and runtime checkpoint

Font B is repair26accepted pending signing;16fixes remain committed.
Final record: css-font-threshold-fix-v1/verification-final-v1.json.
No commit hash is claimed: configured signing retry50594 exits128 with the
1Password buffer error and unchanged HEAD/index. Tooling62files must precede
the standalone2-file Gecko/WPT commit; no other fixes belong in that commit.

Two new preliminary leads have local runtime evidence, without repairs:

- Opacity/pointer-events descendant touch-action: one native APZ failure,
  four passing mode controls and existing zero-opacity control;74stablepins.
  css-breadth-probes-round21-v1/ROOT-OPACITY-RESULTS-v1.json.
- Private-use text emphasis: seven missing-mark observations and five exact
  controls with a loaded, identical-glyph font;70stablepins.
  css-breadth-probes-round21-v1/ROOT-TEXT-EMPHASIS-RESULTS-v1.json.

Both require independent normative/native/known-issue adjudication. Neither
changes accepted repair counts. Timeline clean formal replay passes; deep root
and independent formal acceptance remain pending.


### Independent lead review and font A replay checkpoint

Marker, opacity/touch and private-use emphasis have passed independent defect
adjudication and root authenticated replay; repairs/WPT/formal gates remain.
They are not included in the26accepted pending repairs. Multicol inline-filter
and highlight registered-value leads remain static, with probes prepared.

Font A native matrix is active, with original failures reproduced. Its complete
source-only proof replay22160 passes; independent full review remains required.
Timeline deep root review is complete and independent formal review is active.
There are still16committed fixes; no new commit hash or push is claimed.


### Timeline repair27 accepted; font A final cleanup gate

Pseudo-timeline logical-axis repair is accepted pending signing:42preceding
source/doc files, then the3-file Gecko/WPT patch. Authoritative record:
css-timeline-pseudo-axis-fix-v1/verification-final-v1.json. Counts:16committed
fixes,27fully accepted repairs pending configured signing.

Font A four-way matrix and independent formal/native review pass. A final unused
math.h cleanup requires refreshed build/WPT/lint and source binding; these are
active, so A is not counted yet. Its patch remains separate from font threshold B.

Highlight and inline-filter multicol probes each reproduce4predicted discrepancies
with24and20controls respectively. Their independent adjudication/repair gates
remain, and neither receives an accepted-repair count or commit hash yet.


### Font priority accepted; breadth scouts reproduced three leads

Font A is accepted repair28pending configured signing. Final build/WPT/lint
cycle76289 exits0:26A and38B subtests pass, all80raw result identities/outcomes
match the prior combined run,53pins stay fixed; lint reports0errors and one
ignored-WPT warning. Original/A-only/B-only/AB matrix proves the repairs work
independently. The final6-file patch applies at original base and HEAD.

The v2 source refresh changes only the unused header include and count labels.
Root authenticated93inputs/180receipts and independently checked57unchanged
native/oracle/mutation receipts; four generated translation units remain exact.
Independent full replay44525 and root verification of187review inputs pass.
The32general Lean theorems/11semantic witnesses and full five-consumer/global
scope are retained. Counts mean53628harness rows/30204consumer-entry rows,
not nested invocations. Provider, numeric, lifetime and platform boundaries
remain explicit. Source-only96-path companion precedes the6-file repair.
Final record: css-font-priority-fix-v1/verification-final-v2.json.

Composition run40649 reproduces3discrepancies among16observations with34stable
pins: composite-only updates leave both the getter and rendered value unchanged.
The null-target empty-property case removes CSS parsing as a prerequisite.
Value-changing/default-composite, ordered folds and commit-prefix controls pass.
Bug1778407 comments2–4 already report the symptom; no novelty claim is made.
Independent review is active. ROOT-COMPOSITION-v1.json retains root raw review.
Highlight4/28 and multicol4/24discrepancies also have active independent review.

Round23 font variation scout is frozen and root-read/replayed:131closed files.
Ranked leads are FreeType cast-before-clamp, optical-auto/face-descriptor order,
known font-size-adjust optical sizing, and feature-map/lifecycle invariants.
The first needs a complete native sanitizer gate and Linux/Android rendering;
Mac uses a different clamping path. Optical precedence needs normative review.
All remain static hypotheses or assurance targets. ROOT-FONT-VARIATIONS-SCOUT-v1.json
records the scope; no browser/native bug acceptance is inferred from arithmetic.

Zoom independent review is accepted as defect adjudication, with root replay;
root-rlh scaled/unscaled provenance is the narrower proposed first repair.
Marker, opacity and private-use emphasis remain separate accepted defect leads
requiring implementation/WPT/formal work. No new commit hash exists:16fixes are
committed and28repairs accepted pending configured signing. No push or signing
retry was made in this checkpoint. All root browser/build processes are terminal.

## Collapsed flex items: native gates complete, review/formal pending

No commit yet; excluded from the 30 accepted repairs awaiting signing.
Round28 static inspection found that collapsed struts remain participants in
main-axis distributed spacing and auto-margin allocation. The three-file patch
contains only nsFlexContainerFrame.cpp and two relevant WPT files.

- Paired WPT: 78 FAIL / 72 PASS become 150 PASS.
- Additional candidate controls: 240 PASS, including logical/reversed axes,
  ordinary zero-size participants and visible automatic margins.
- Existing checks: 82 PASS; build/format pass; lint zero errors/two ignored warnings.
- Standalone patch applies at base and HEAD; no isolated-base build performed.
- Patch: `css-flex-collapsed-alignment-fix-v1/fix-candidate-v1.patch`.
- Evidence: `css-flex-collapsed-alignment-fix-v1/ROOT-NATIVE-WPT-v1.json`.
- Independent native review and full formal companion/review are pending.

Column intrinsic cross-size and collection-stage gap leads are separate and
unaccepted. Large hyphenation-limit saturation is a reproduced range-policy
question, not another accepted defect or repair.


## Page-selector names: native gates complete, review/formal pending

No commit yet; excluded from the 30 accepted repairs awaiting signing.
The page-rule matcher accepted selectors with a different name from its lookup
bucket, affecting both applicability and specificity. The candidate passes the
bucket name into the matcher and filters before computing the maximum.

- Paired new print tests: 10 FAIL / 8 PASS become 18 PASS, with 47 unchanged
  inputs; only two Rust files and two binaries differ across the 51-pin pair.
- Six existing print regressions pass on original and candidate.
- Saved failing pages have a 20px green square displaced downward by exactly
  96px; all candidate test/reference images agree and retain the square.
- Build exits 0 (existing build-monitor KeyError diagnostics retained); format
  exits 0; lint has zero errors and six ignored-HTML warnings.
- Proposed standalone patch has two Rust files and six WPT files. It applies
  at original base and HEAD. Base stylist.rs retains its unrelated older scope
  code; the complete PageRuleMap implementation matches the current candidate.
  No isolated-base build was performed.
- Patch: css-page-selector-name-fix-v1/fix-candidate-v1.patch.
- Receipt: css-page-selector-name-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Independent native review and full formal companion/review remain pending.

Signing retry71799 returns commit exit128: 1Password failed to fill whole buffer.
HEAD and the original twelve staged RGB companion files remain unchanged;
signing stays enabled. No new commit hash or push is claimed.

## Nowrap partitions: verifier-development lead reproduced in the browser

The language proof producer found a false arbitrary-partition glyph/sink equality
obligation using actual extracted native code. Root executed its standalone
probe and independently rederived 12 discrepancies and 60 passing controls from
character rectangles, computed styles and intrinsic widths. A nowrap inline in
a wrapping block breaks under break-all/anywhere: whole text has four lines,
while adjacent/nested partitions have two, where the independent nowrap oracle
requires one. Capitalization variants reproduce; block-nowrap and normal/keep-all
controls pass. Forty source/evidence/binary pins stay fixed.

This is a combined-worktree browser observation, not an original/release-browser
run or a completed Lean proof of a bug. The separate extracted original and
language-candidate evidence is retained. No repair or accepted count yet;
normative/native/known-issue adjudication and a standalone WPT repair are next.
Receipt: css-nowrap-partitions-probe-v1/ROOT-BASELINE-v1.json. The language proof
scope is unchanged, and its separate LF counterexample remains unresolved.

## Nowrap publication repair: native gates complete

No commit or formal acceptance yet; excluded from the 30 accepted repairs
awaiting signing. The language verifier's retained counterexample led to a
separate suppression repair in both AppendText publication paths. The helper
uses chunk-relative positions: INITIAL governs zero and INSIDE governs later
positions, preserving allowed breaks before the nowrap inline.

- New exact WPT pair: 36 FAIL / 133 PASS becomes 169 PASS. All 24 input
  identities stay fixed within each run; only one C++ file and two binaries
  differ between runs.
- Paired shared-service regressions: 724 PASS / 17 OK before and after, across
  21 files. Of 71 identities, the same three differ between runs.
- Build exits 0 with four retained build-monitor KeyError diagnostics. Format
  exits 0; unrelated changes restored exactly. Lint has zero errors and one
  ignored-HTML warning.
- Standalone patch contains nsLineBreaker.cpp and one WPT. It applies and
  reverses exactly at original base and HEAD, without language or hyphenation
  prerequisites. No isolated-base build or release-browser test was performed.
- Patch: css-nowrap-partitions-fix-v1/fix-candidate-v1.patch.
- Receipt: css-nowrap-partitions-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Proposed full proof: css-nowrap-partitions-fix-v1/FORMAL-TARGET-DRAFT.md.
  Independent review and formal production/review remain pending. Existing
  language-only scope and LF/partition counterexamples are preserved.

The source-only PUA emphasis replay also passes freshly under root execution;
84 deterministic JSON/text receipts match the producer exactly. Only elapsed
cost timings differ, with identical units/draw counts/output sizes. This is
reproducibility evidence, not final formal acceptance. Root record:
css-text-emphasis-pua-root-review-v1/ROOT-REPLAY-v1.json.

## Negative ligature advance: browser baseline and candidate patch

No commit or final acceptance yet. Root tested an excluded numeric premise in
the PUA emphasis model and reproduced unsigned width expansion in
ComputeLigatureData. The native candidate uses a signed 64-bit quotient and
products, preserving the existing truncation and final-part remainder policy.

- New WPT baseline: 4 FAIL / 44 PASS, across text-node/span partitions and
  LTR/RTL. A retained standalone font creates negative advances through GPOS.
- Baseline shaping regressions: 24 PASS and 2 existing expected FAIL across
  26 files. Candidate browser gates remain pending while the build runs.
- Separate three-file patch: gfxTextRun.cpp, WPT HTML, and its test font.
  It applies and reverses exactly at original base and HEAD; no isolated build.
- Patch: css-negative-ligature-fix-v1/fix-candidate-v1.patch.
- Packaging receipt: css-negative-ligature-fix-v1/standalone-apply-v1.json.
- Tooling/font generator/proof must precede the eventual standalone fix commit.
  Independent native and formal review remain required. No acceptance increment.

PUA emphasis v1 has a separate root-identified universal dispatcher-to-plan
gap. It remains unaccepted; v2 correction retains the full approved scope.
Sticky positioning has three reproduced hypotheses awaiting additional controls
and independent adjudication, not three accepted repairs.

### Negative ligature candidate native gates complete

The candidate passes all 48 new WPT subtests (4 baseline failures repaired).
All 26 regression outcomes/expectations are unchanged: 24 PASS and 2 existing
expected FAIL. Build and format pass; lint reports zero errors and one ignored
HTML warning. The final three-file patch SHA-256 is
f82e0f68140c9754ad7db4bdff4f978457b9f8caccdfd71a10c9e37a73203f71.
Final native record: css-negative-ligature-fix-v1/ROOT-NATIVE-WPT-v1.json.
Independent native/font/oracle review and formal acceptance remain pending.
No commit hash exists yet and the accepted-repair count is unchanged.

## Sticky auto inset: native gates complete, review/formal pending

No commit or final acceptance yet. The candidate constructs the sticky view
using zero for auto insets and applies end reduction when either side is active.
Movement still tests the original specified-inset flags.

- Corrected exact WPT pair: 18 FAIL / 198 PASS becomes 216 PASS.
- V1 had two extra negative-zero expectation mistakes; preserved evidence and
  correction are in css-sticky-auto-inset-fix-v1/ORACLE-CORRECTION-v1.json.
- Seventeen existing sticky files retain 30 PASS / 2 expected FAIL / 8 OK.
  Fourteen shared view-timeline files retain 17 PASS / 14 OK.
- Build and format pass; lint zero errors, one ignored-HTML warning.
- Two-file patch: StickyScrollContainer.cpp and one WPT. Exact apply/reverse
  checks pass at original base and HEAD; no isolated build.
- Patch SHA-256: 001466c48760c278bc639cdb0ae2e8fe2ddb31886fd357f51d51536368b5fc85.
- Receipt: css-sticky-auto-inset-fix-v1/ROOT-NATIVE-WPT-v1.json.
- Independent review and formal companion remain pending; proposed full scope
  is in FORMAL-TARGET-DRAFT.md. Tooling/proof precedes the standalone fix commit.

The separate containing-block writing-mode and nested-invalidation leads remain
unrepaired. No acceptance-count increment. Signing retry41988 still fails with
the same 1Password error; HEAD and the twelve staged RGB companion files are
unchanged. Details: css-negative-ligature-fix-v1/SIGNING-RETRY-v1.json.

## Sticky writing-mode repair: independent patch matrix complete

No commit or full formal acceptance yet. Standalone patch:
`css-sticky-writing-mode-fix-v1/fix-candidate-v1.patch` (one Gecko file and one WPT).
Native/WPT receipt: `css-sticky-writing-mode-fix-v1/ROOT-NATIVE-WPT-v1.json`.

| Sticky source variant | Auto-inset WPT | Writing-mode WPT |
| --- | --- | --- |
| Original | 198 pass, 18 fail | 912 pass, 168 fail |
| Auto-inset only | 216 pass | 912 pass, 168 fail |
| Writing-mode only | 198 pass, 18 fail | 1,080 pass |
| Both | 216 pass | 1,080 pass |

All four builds succeed. Final combined source and binary are restored.
Existing sticky and view-timeline results are unchanged. Full proof companions
remain queued; independent native/spec/oracle review is root-accepted.

## Shadow-context depth: reproduced lead, no repair yet

Eight failing rows and 72 controls in the root's 80-case browser probe match the
static scout prediction. Both margin-left and an unregistered custom property
choose the wrong context at depths 8/9 when unrelated part-rule maps are present.
Fresh construction agrees with the dynamic result. Evidence:
`css-shadow-context-depth-probe-v1/ROOT-BASELINE-v1.json`.
Independent adjudication and representation design precede a fix; excluded from
the accepted-repair count. Discovery came from static analysis, not a Lean proof.

## Recursive attribute fallback preparation committed

`7822bb6d17b1381cdb3e56deb20c5ec3e078adec` contains only `Cascade::update_attributes_map` and its sixteen-case WPT.
Proof companion: `31265260cc3daa2bbea93c237a9491b6f2afcaa4`; browser evidence: `222c13771e052dae71bb6f62cc35e1a0522a91c3`.
Ten failures become passes; seventy existing checks pass. Three unchanged
type-eligibility diagnostics remain failing. Fresh root Lean replay passes
54 theorem audits (38 new) and rejects four semantic mutants. This is a finite
worklist/preparation model with manual source binding; native parser, provider,
observer and graph composition remain open. The browser pair used the shared
experimental tree; the exact commit excludes those unrelated changes.
See [acceptance](../css-attr-fallback-preload-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-fallback-preload-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## MathML token range origin committed

`f843fd7568f30e14e664c37c36544d8d88e8c1bb` changes only `GetTrimmedOffsets` and includes two regression WPTs.
Review/evidence companion: `6eb5a90e3fa3b6128ddd6397d9dae9f1ab34b88d`.
Eight original failures become passes; all 26 new and 260 existing checks pass.
Original/candidate builds, repeated candidate results and lint passed. The
independent source review checks 128 branch combinations and distinguishes
significant trailing trimming. This is not a Lean proof of native geometry.
Pre-reflow/intrinsic measurement, element-box sizing and broader cache lifetime
remain separate. Browser pairing used the shared experimental tree.
See [acceptance](../css-mathml-tab-cache-wpt-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-mathml-tab-cache-wpt-v1/ROOT-COMMIT-CHECK-v1.json).

## Typed attribute fallback eligibility committed

`e3ba54f6f826fe265eb5bc4731f66f64465dd47c` contains only three Rust files and the twelve-case WPT.
Review and browser evidence precede it in `30c8dfeb4b746104b53ad5bc6440c1d53734f570`.
Five new-case failures and three retained diagnostics become passes; all 183
checks pass. Build and lint pass (zero errors, two warnings). The earlier
generic-parser model has fifteen theorem audits; this integration adds no
new theorem and does not close native parser, provider or graph admission.
The exact isolated patch excludes unrelated experiments; browser pairing used
the shared tree. Additional parse cost is unmeasured.
See [acceptance](../css-attr-typed-eligibility-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-typed-eligibility-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## Attribute-only non-custom dependencies committed

`3892ab844694fedd987f5ce1dd2165f53fc2dbed` deletes the lexical-VAR early return in
`Cascade::maybe_note_non_custom_dependency` and adds a ten-case WPT.
Review/browser companion: `0db19774e6f2bf6692790459f8e6e54ca426e366`.
The ten new and 183 prior checks pass. Four baseline failures improve across
the scoped WPT and diagnostic; three resolved-unit metadata failures remain.
Build passes; warning-enabled lint has zero errors and one ignored-WPT warning.
Independent syntax and source/oracle review pass. No new native graph theorem
is claimed; discovery came from manual analysis of formal admission gaps.
See [acceptance](../css-attr-noncustom-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)
and [commit check](../css-attr-noncustom-browser-v1/ROOT-COMMIT-CHECK-v1.json).

## Resolved relative-unit summaries committed

`58200fa81a6f92f92a1898ba2866a2fbcbac0daa` contains one Rust file and the 21-case WPT. It restores relative-unit
dependency metadata when storing resolved attribute and universal values. The
final formatted build passes all 227 checks; 13 baseline failures are repaired.
Evidence and independent reviews precede it in `03bad7f708329254a9af2073f0b4106ba557e914`. Lean selected-output
composition is conditional on token/provider correspondence; full tokenizer and
graph proofs remain open. Incomplete env payload scans retain their previous
behavior, and added scan cost is unmeasured.

## Token-category dependency repair committed

`26e0fa16e89eacd9fd9cab0ce6bb1be813d9e406` contains the Dimension-only guard and its 14-case WPT.
Identifiers, URLs, at-keywords and hashes no longer acquire false relative-unit
dependencies from their spelling. Seven baseline failures are repaired; all
241 checks pass. Evidence precedes the repair in `2e1f5f62c8a6325679a83adc7f637e104c488bf7`. The patch applies
and reverses against retained upstream/main `976279105b2e78b8666a959eb3f25c9176cefaf8`
without earlier local fixes; that isolated base was not built or browser-tested.
The discovery came from manual source/spec admission review, not a new Lean
counterexample. Full tokenizer and graph proofs remain open.
