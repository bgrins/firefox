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
| Easing animation-driven context | Three new tentative callbacks prepared and statically checked; no browser execution or new bug claim |
| Min/max contextual infinity | Individual 472-case comparison repairs 14 targets; two legacy failures preserved; 32 authored checks pass; uninstalled proposal |
| Log special values | Individual 102-case comparison repairs 15 targets and all 102 pass; 24 authored checks pass; uninstalled proposal |
| New Lean math models | Min/max winner guard: 14 theorem audits and four rejected false claims; log dispatch: 12 audits and three rejected false claims; canonical library coverage unchanged |
| Combined math baseline | Fresh 578-callback run: 543 PASS, 35 FAIL, including all 33 targets; 16 page endings, 561 control/ending signatures; combined candidate not run |
| Build-cache cleanup | Twelve obsolete Lean build caches removed; 7.99 GiB allocated space reclaimed; source and evidence retained |
| Held provider and other prototypes | Incomplete integration work; held provider is the sole tracked edit, and 68 prototype files remain untracked at their working paths with committed recovery copies |

Root independently replayed the combined baseline raw stream after actual
session 11014, terminal f93d6f, exit 0. The four new interaction cases fail on
the final value comparison at a 16px font basis, after setup succeeds. Source,
application, canonical state and process cleanup were verified. Individual
comparisons were performed on the shared branch with its documented prior
fixes and held provider; they do not establish dependency-free cherry-picks.

The combined candidate remains unfinished. Continue with a fresh binding after
this research checkpoint, then publish each native repair with only its native
change and WPT coverage. The log commit must remove five obsolete expected-FAIL
annotations. Add the signed native commits to the ledger only after acceptance.

The [fresh untracked audit](../css-untracked-audit-user-followup-20261029-v2.json)
found exactly 563 expected paths and no missing or unexpected paths. All 68
project files match recorded contents, modes, identities and committed recovery
copies. The remaining 495 files match names and filesystem metadata; their
contents were not read or staged. They comprise .claude (5), tabcanvas (183),
claude-docker (286), perf-lab (20) and test-results (1).

This checkpoint records completed research separately from native acceptance.
Its commit outcome is recorded by the driver in result.json. No push or Try run
is authorized by this checkpoint.
