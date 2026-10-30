# Branch work inventory

Branch `stylo-bloom-verification-2`, HEAD `ecfe313d582a335c04d80bfd360fd3a591defdb7`. This is local work, not upstream landings. All 149 accepted native commit objects were verified as ancestors of HEAD. Held ID 120 and two test-only repairs are excluded from that count.

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

[Individual fixes, commit IDs and prerequisites](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).

| Other work | Current status |
| --- | --- |
| Bloom milestones 1–6 | Complete within their documented bounds. |
| Canonical CSS Lean library | Committed nested HEAD `162b20fb7c53`; 11,840 audits, 12,438 cases, 173 rejected false cases, 2,155 fingerprints. Scoped handwritten models; no full CSS or Stylo refinement claim. |
| Contextual easing | 315-case comparison repairs 41 targets; isolated Servo checks pass with documented adaptations. No accepted native fix. |
| Duration candidate | Combined timing/scheduling repair passes 50 normative/reactivation callbacks, the infinite-duration reftest, two reduced callbacks and restyles (162 PASS/eight expected FAIL). Original application and sources restored. Reduced matching-only discrimination remains pending; no accepted native fix yet. |
| Duration formal models | Dispatch-attempt model: six theorem audits/five false controls. Queue bookkeeping companion: 13 audits/six false controls. Conditional handwritten models; no native refinement or canonical coverage increment. |
| Duration diagnostic tooling | Completed instrumented pair: original two PASS, matching-only two FAIL; 13 bounded deferred/coalesced intervals share six seeds. Original has none under the same criterion. Diagnostic evidence has explicit scheduling and causality limits. |
| Min/max and logarithm candidates | Individual, combined and provider-free comparisons complete. Combined comparison repairs 33 targets, preserves two legacy failures, passes 60 authored checks. Two separate native/WPT commits remain pending. |
| Additional math models | Min/max 14 theorem audits/four negative controls; log 12/three; literal-zero policy 16/four. Canonical coverage unchanged. Literal-zero behavior requires spec/interop clarification. |
| Test-only repairs | Two committed repairs, excluded from native bug count. |
| Held integration | Sole tracked modification is `servo/components/style/custom_properties.rs`. Not ready for native acceptance. |
| Prototype files | 53 WPTs and 15 native/support files remain untracked at working paths; all 68 match committed recovery copies. |
| Unrelated files | 495 expected paths: .claude 5, tabcanvas 183, claude-docker 286, perf-lab 20, test-results 1. Metadata unchanged; contents not read or staged. |
| Build cache cleanup | Earlier cleanup reclaimed 7.99 GiB from 12 obsolete Lean caches. Verified temporary application backups were removed after each completed restoration, including 1,008,605,176 bytes from the latest broader trial. |
| Completed research publication | Still pending. Last signed checkpoint attempt failed in 1Password with `failed to fill whole buffer`; no new signing attempt or unsigned fallback performed during this audit. |

Staging is empty. The fresh [post-run audit](AUDIT.json) found no unexpected or missing untracked paths and verified prototype bytes against committed recovery objects and unrelated filesystem metadata. Accepted-commit ancestry was verified in the earlier audit; HEAD remains unchanged. Ignored research artifacts are separate from the 563-file Git untracked listing.

[Current roadmap](PLAN.md). The table records 149 accepted native commits; completed research and candidate validation are listed separately and do not increase that count.
