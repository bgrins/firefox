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
| Contextual duration candidate | Repairs five bounded failures, but four first reads remain stale. Completed instrumented run localizes late child Pending work during the flush. Sources/app restored. The new same-element comparison passes both callbacks, but its timing-source oracle needs specification/interoperability clarification. Not accepted. |
| Duration formal models | Dispatch-attempt 6 theorem audits/5 false controls; QueueState 13/6; earlier feedback two-cycle companion 5/2; new finite-chain completion model 17/7, independently reviewed. New parity/oracle bridge adds 9 audits/4 false controls using the existing evaluator. No native refinement claim. |
| Duration diagnostics | Complete native trace and exact 258-query/204-value join. Paired same-element run changes acyclic opacity .75 to .545455 and stepped feedback font 32 px to 16 px. Literal controls pass; cyclic endpoint remains unasserted. Full restoration independently verified. Finite-depth original completed: four contextual FAILs, literal/setup calibration passes and four complete records. Candidate comparison is running; no result yet. |
| Min/max and logarithm candidates | Combined/provider-free comparisons complete: 33 repaired targets, 60 authored passes, two preserved legacy failures. Two native/WPT commits pending preceding research publication. Both publication recipes now exist; logarithm adaptation independently reviewed and disabled pending actual bindings. |
| Additional math models | Min/max 14 theorem audits/4 false controls; log 12/3; literal-zero policy 16/4. Canonical coverage unchanged. |
| Test-only repairs | Two committed repairs, excluded from native bug count. |
| Held integration | custom_properties.rs is the held integration change. An owned three-source candidate overlay is temporarily installed for the running depth comparison; restoration is pending. |
| Prototype files | 53 WPT and 15 native/support untracked working copies, byte-identical to committed recovery copies. |
| Unrelated local files | 495 expected paths; metadata unchanged, contents untouched. Nested CSS Lean has only untracked .DS_Store. |
| Cleanup | Prior obsolete Lean-cache cleanup reclaimed 7.99 GiB. Completed same-element backup of 1,008,605,176 bytes removed after verified restoration. The running depth experiment has a new owned backup; retain it until restoration verification. |
| Completed research publication | Latest V79 signing failed in 1Password. All 4,456 selected research paths remain uncommitted; repository state independently verified unchanged. Later comparisons, oracle bridge, upstream source review, log publisher and Safari/depth evidence are also uncommitted. |

[Current roadmap](PLAN.md). Ignored research artifacts are separate from the 563-file Git untracked listing.
