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

| Other work | Current status |
| --- | --- |
| Contextual duration timing trial | Four-source build completed; original 1 PASS / 6 FAIL becomes 2 PASS / 5 FAIL, three OK endings and seven calibrated records. Masked update repaired; same-element rendered/effect outputs match original Firefox and Chrome; all four descendant first reads still fail. Comparison failure preserved, all sources/app restored. Not accepted. |
| Descendant completion | New sample trajectories equal the earlier candidate: depth 1/2 correct by frame 1, depth 4 by frame 2, depth 8 stale through frame 3. Chrome passes every first read. Later frames do not satisfy first-read correctness or identify native pass counts. |
| Same-element timing policy | New manager uses pre-own-effect timing while keeping composed keyframe/effect inputs. Sampled outputs now agree with Chrome; Firefox computed CSS still differs. Initial own-input policy and full normative update trace remain unresolved. |
| Masked update isolation | One-line normal-admission experiment and final-only standalone WPT prepared and statically checked, not executed. Default typed arithmetic true is joined to HEAD/original build. Minimal source necessity, unrelated-restyle behavior, API ownership and performance remain to test. |
| Parent publication implementation | Task-transfer and unpublished-style/publication prerequisites are reviewed artifact patches. Extracted mock tests pass; no real Stylo build, exact-target compositor preparation or staged child-release driver yet. Not a completion fix. |
| Duration formal work | Dispatch 6 audits/5 false controls; QueueState 13/6; feedback companion 5/2; finite-chain completion 17/7; parity bridge 9/4; ranked DAG 23/6. Isolated models, no canonical coverage increment or native refinement proof. |
| Contextual easing | Prior 315-case comparison repairs 41 targets; isolated Servo checks with documented adaptations. Not accepted; deferred behind concrete duration work. |
| Min/max and logarithm | Combined/provider-free comparison repairs 33 targets with 60 authored passes and two preserved legacy failures. Separate reviewed native/WPT publication recipes await successful research checkpoint and fresh admission. No new accepted IDs. |
| Other math models | Min/max 14 audits/4 false controls, log 12/3, literal-zero policy 16/4. Canonical coverage unchanged. |
| Canonical CSS Lean | Committed nested HEAD 162b20fb7c53; 11,840 audits, 12,438 cases, 173 rejected false cases, 2,155 fingerprints. New experimental models are separate. |
| Bloom milestones | Milestones 1–6 complete within documented bounds. |
| Cross-engine evidence | Chrome 156: same-element 1 PASS / 1 FAIL, four depths PASS, masked callback PASS. Exact fixtures/records retained. Safari automation admission failed without fixture execution or preference changes. |
| Native/application state | Latest four-source trial and prior temporary overlays restored; held custom_properties.rs remains the sole tracked native edit. No new acceptance from this phase. |
| Test-only repairs | Two committed repairs, excluded from native fix count. |
| Untracked project prototypes | 53 WPT plus 15 native/support working copies retain committed recovery copies. All 68 project bodies match their committed recovery copies in the final post-bootstrap audit. |
| Unrelated local files | All 495 expected paths retain their recorded metadata in the final post-bootstrap audit. |
| Cleanup | Latest owned 1,008,605,176-byte candidate backup verified and removed. Prior obsolete Lean-cache cleanup reclaimed 7.99 GiB. Portable browser cleanup status follows the latest explicit root receipt, not historical V85 assumptions. |
| Specification tooling | webspec-index 0.14.0 installed and pending-style query completed. Full first-getter normative trace remains INCONCLUSIVE. |
| Research commits | V80 signed attempt failed in 1Password with no commit/state change. Fresh V81 research signer preparation is disabled pending final inventory/admission. Existing local-commit authorization persists; no automatic retry of old owners or unsigned substitution. |

[Current roadmap](PLAN.md). Ignored research artifacts are separate from the Git untracked census.
