# Local branch work

149 accepted native fix commits across 150 tracked IDs; held ID 120 and two test-only repairs are excluded. These are local commits, not upstream landings. [Individual commit IDs and prerequisites](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).

| Accepted fix area | Commits |
| --- | ---: |
| Selectors, Bloom filters and scoping | 12 |
| Cascade, layers and shorthands | 6 |
| Parsing, tokens and CSS math | 31 |
| Attributes and custom properties | 19 |
| Animations, timelines and transitions | 18 |
| Text and fonts | 16 |
| Layout, sizing and positioning | 23 |
| Container queries | 3 |
| Colors, images, SVG and shapes | 8 |
| CSSOM geometry and hidden layout | 13 |
| **Total** | **149** |

| Other work | Status |
| --- | --- |
| Bloom milestones 1–6 | Complete within documented bounds. |
| Canonical CSS Lean | Committed nested HEAD 162b20fb7c53; 11,840 audits, 12,438 cases, 173 rejected false cases, 2,155 fingerprints. |
| Contextual easing candidate | 315-case comparison repairs 41 targets; isolated Servo checks pass with documented adaptations. Not accepted. |
| Contextual duration candidate | Repairs five bounded failures, but four first reads remain stale. Completed instrumented run localizes late child Pending work during the flush. Sources/app restored. Not accepted. |
| Duration formal models | Dispatch-attempt 6 theorem audits/5 false controls; QueueState 13/6; earlier feedback two-cycle companion 5/2; new finite-chain completion model 17/7, independently reviewed. No native refinement claim. |
| Duration diagnostics | Complete native trace and exact 258-query/204-value join. New original-only same-element run reproduces acyclic stale opacity, calibrates literal controls and records stepped feedback without an endpoint oracle. State preserved. |
| Min/max and logarithm candidates | Combined/provider-free comparisons complete: 33 repaired targets, 60 authored passes, two preserved legacy failures. Two native/WPT commits pending preceding research publication. |
| Additional math models | Min/max 14 theorem audits/4 false controls; log 12/3; literal-zero policy 16/4. Canonical coverage unchanged. |
| Test-only repairs | Two committed repairs, excluded from native bug count. |
| Held integration | custom_properties.rs remains the sole tracked modification. |
| Prototype files | 53 WPT and 15 native/support untracked working copies, byte-identical to committed recovery copies. |
| Unrelated local files | 495 expected paths; metadata unchanged, contents untouched. Nested CSS Lean has only untracked .DS_Store. |
| Cleanup | Prior obsolete Lean-cache cleanup reclaimed 7.99 GiB. Latest restored application backup of 1,008,605,176 bytes removed after verification. |
| Completed research publication | Latest V79 signing failed in 1Password. All 4,456 selected research paths remain uncommitted; repository state independently verified unchanged. Later comparison preparation is also uncommitted. |

[Current roadmap](PLAN.md). Ignored research artifacts are separate from the 563-file Git untracked listing.
