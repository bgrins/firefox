# Branch work inventory at first-read trace build start

Branch `stylo-bloom-verification-2`, HEAD `ecfe313d582a335c04d80bfd360fd3a591defdb7`. This is local work, not upstream landings. Earlier audits verified all 149 accepted native commit objects as ancestors of this unchanged HEAD. Held ID 120 and two test-only repairs are excluded from that count.

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
| Duration candidate | Prior broader validation passes. New comparison repairs five bounded failures and preserves four controls (nine PASS), but four first reads remain stale. Immediate freshness is required before native acceptance. The prior comparison restored sources/app; a new instrumented trial is now running with temporary overlays. |
| Duration formal models | Dispatch-attempt model: six theorem audits/five false controls. Queue bookkeeping companion: 13 audits/six false controls. Conditional handwritten models; no native refinement or canonical coverage increment. |
| Duration diagnostic tooling | Native instrumentation, final configured VFS syntax checks, authored getter-order table, compiler-derived property IDs and strict trace/record joiner are complete. Root admission passed and owner 61350 started `mach build binaries -j2` (PID 75095). Five source overlays and an owned original backup are active. No build terminal, browser result or restoration exists for this trial at the cutoff. Exact old fixtures retain their nine bounded PASS verdict and four first-read mismatches. Stronger assertion successors remain unexecuted. |
| Min/max and logarithm candidates | Individual, combined and provider-free comparisons complete. Combined comparison repairs 33 targets, preserves two legacy failures, passes 60 authored checks. Two separate native/WPT commits remain pending. |
| Additional math models | Min/max 14 theorem audits/four negative controls; log 12/three; literal-zero policy 16/four. Canonical coverage unchanged. Literal-zero behavior requires spec/interop clarification. |
| Test-only repairs | Two committed repairs, excluded from native bug count. |
| Held integration | Before the active experiment, `servo/components/style/custom_properties.rs` was the sole tracked modification. It remains held while five additional source paths are temporarily overlaid by the runner. No native acceptance. |
| Prototype files | 53 WPTs and 15 native/support files remain untracked at working paths; all 68 match committed recovery copies. |
| Unrelated files | 495 expected paths: .claude 5, tabcanvas 183, claude-docker 286, perf-lab 20, test-results 1. Metadata unchanged; contents not read or staged. |
| Build cache cleanup | Earlier cleanup reclaimed 7.99 GiB from 12 obsolete Lean caches. The latest verified temporary application backup (1,008,605,176 bytes) was removed after restoration. |
| Completed research publication | V78 signing also failed in 1Password (86468/d7968c/1, Git128); HEAD/index/epoch were preserved and the lock released. Completed pending research is still unsigned. No automatic retry or unsigned fallback. |

The saved V78 audit found empty staging and exactly 563 expected untracked paths (68 prototypes plus 495 unrelated), with no missing or unexpected paths. The latest [signing terminal](../css-research-checkpoint-20261029-v78-root-terminal.json) records unchanged HEAD/index/epoch and absent transition lock. This roadmap performs no live audit. Ignored research artifacts are separate from that Git untracked listing; the current five-source experiment must report its own restoration. The worktree is currently experimental, not claimed restored.

[Current roadmap](PLAN.md). The table records 149 accepted native commits; completed research and candidate validation are listed separately and do not increase that count.
