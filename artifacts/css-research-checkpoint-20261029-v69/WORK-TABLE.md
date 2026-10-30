# Branch work checkpoint

The branch has 149 accepted native fixes across 150 tracked IDs. ID 120 is held
and excluded. All 149 native commit objects were verified as ancestors of
`ecfe313d582a335c04d80bfd360fd3a591defdb7`; the ledger matches its committed copy.
These counts describe accepted local work, not upstream landings.

| Accepted native area | Fixes | Example commit |
| --- | ---: | --- |
| Selectors, Bloom filters and scoping | 12 | `d855b3483b49` saturation tracking |
| Cascade, layers and shorthands | 6 | `074086719e44` logical all ordering |
| Parsing, tokens and CSS math | 31 | `2d18f8b4a4d7` pow exceptional values |
| Attributes and custom properties | 19 | `0f40801f1418` registered-value zoom |
| Animations, timelines and transitions | 18 | `9e99cf9e4c88` shadow move preservation |
| Text and fonts | 16 | `975e651729ba` contextual line-height |
| Layout, sizing and positioning | 23 | `c13f212eb284` page specificity |
| Container queries | 3 | `ef3d32280505` size invalidation |
| Colors, images, SVG and shapes | 8 | `fa9dff982cec` SVG unit conversion |
| CSSOM geometry and hidden layout | 13 | `9c2257a80e3f` embedding-frame refresh |
| **Total** | **149** | |

The [full individual table](../css-pow-special-value-acceptance-publisher-v2/readout/README.md)
and [machine ledger](../css-pow-special-value-acceptance-publisher-v2/readout/ACCEPTED-FIXES.json)
include commit IDs, prerequisites and held status. Two test-only repairs,
`ae4db18e4b3e` and `5cdd697e02d2`, are excluded from the native count.
Area grouping is not a security or severity assignment.

| Other work | Evidence and current boundary |
| --- | --- |
| Bloom milestones 1–6 | Completed within documented bounds; historical replays are not universal proofs of current native source |
| Canonical CSS Lean library | Nested HEAD `162b20fb7c53`; recorded 11,840 audits, 12,438 cases, 173 rejected false cases and 2,155 fingerprints; handwritten scoped semantics, not full CSS or browser refinement |
| Contextual easing | Completed 315-case Gecko comparison repairs 41 targets; isolated Servo checks pass with documented adaptations; no accepted native fix |
| Easing animation-driven context | Original three callbacks fail initial unsupported-syntax admission (known bug 2037743); no freshness finding. Ordinary-property easing probe is static; duration probe avoids that feature gate |
| Animation-driven duration | Completed three-case original 2 PASS/1 FAIL becomes 3 PASS under V1; restored. Guarded V2 built and passed all 50 normative callbacks plus the reftest. Restyles preserved 162 PASS/eight expected FAIL apart from four validated timestamp diagnostics; owner exited 1 before feedback. Source/app restored; no accepted fix |
| Duration scheduling/feedback models | Scoped synchronization with script ownership and conditional feedback two-cycle; no native refinement or convergence claim |
| Original restyle-count baseline | 162 PASS assertions, eight expected failures, zero unexpected; candidate assertion results preserved under the reviewed four-message timestamp projection; no performance-ratio claim |
| Min/max contextual infinity | Individual 472-case comparison repairs 14 targets; two legacy failures preserved; 32 authored checks pass; uninstalled proposal |
| Log special values | Individual 102-case comparison repairs 15 targets and all 102 pass; 24 authored checks pass; uninstalled proposal |
| New Lean math models | Min/max winner guard: 14 theorem audits and four rejected false claims; log dispatch: 12 audits and three rejected false claims; canonical library coverage unchanged |
| Combined math comparison | Fresh original 543 PASS/35 FAIL becomes 576 PASS/2 preserved legacy FAIL across 578 callbacks; 33 targets repaired, all 60 authored checks pass, 561 original control/ending signatures preserved |
| Held-provider independence | Combined candidate rebuilt with the provider reverted to committed HEAD; all 594 full row/ending signatures equal the successful with-provider candidate; both sources and the original app restored |
| Min/max signed-zero tie audit | Inspected folding/runtime paths are sign-aware; proposed ordering defect dismissed, with scoped conversion-path limits |
| Literal-negative-zero boundary | Original observation: four controls pass, two literals yield 0.25 instead of written-spec 0.75; known CSSWG 7472/spec-WPT conflict, no accepted bug |
| Literal-zero policy model | 16 theorem audits and four rejected false claims; independent review clear; finite policy/observer model, no native parser refinement |
| Build-cache cleanup | Twelve obsolete Lean build caches removed; 7.99 GiB allocated space reclaimed; source and evidence retained |
| Held provider and other prototypes | Incomplete integration work; held provider is the sole tracked edit, and 68 prototype files remain untracked at their working paths with committed recovery copies |

Root independently replayed the combined baseline raw stream after actual
session 11014, terminal f93d6f, exit 0. The four new interaction cases fail on
the final value comparison at a 16px font basis, after setup succeeds. Source,
application, canonical state and process cleanup were verified. Individual
comparisons were performed on the shared branch with its documented prior
fixes and held provider; they do not establish dependency-free cherry-picks.

The combined and provider-free comparisons are complete and restored their
source/application state. Neither math repair is accepted or permanently installed.
The reviewed publication payloads preserve two separate native commits: MinMax
source plus two WPTs, then log source plus one WPT and deletion of five obsolete
expected-FAIL annotations. The four integration probes remain research-only.
Provider independence is established for the measured candidate signatures; it
does not establish dependency-free cherry-picks or a provider-free causal
original/candidate comparison. Prior accepted source prerequisites remain.
Literal-zero behavior requires interop/spec clarification before any normalizer
patch; generated negative zero must remain intact. Native ledger updates belong
after actual separately reviewed acceptance.

The [fresh untracked audit](../css-untracked-audit-user-followup-20261029-v4.json)
found exactly 563 expected paths and no missing or unexpected paths. All 68
project files match recorded contents, modes, identities and committed recovery
copies. The remaining 495 files match names and filesystem metadata; their
contents were not read or staged. They comprise .claude (5), tabcanvas (183),
claude-docker (286), perf-lab (20) and test-results (1).

This checkpoint records completed research separately from native acceptance.
V62, V64 and V66 signing attempts failed without publication; V68 was only preflighted.
V69 now includes the completed failed broader candidate, verified restoration and raw-index
refresh, all completed original observations, diagnostic projection, scoped models and
source/spec traces, the current math publication plan and disabled MinMax installer.
Feedback remains unobserved on guarded V2. Earlier publication drafts are historical;
the V70 roadmap supersedes their next-step guidance. Native and canonical proof counts
are unchanged. Future feedback-only templates remain excluded. No push, Try run,
unsigned fallback or native acceptance is authorized by this package.
