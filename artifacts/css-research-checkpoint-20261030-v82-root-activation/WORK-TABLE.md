# Branch work — V88

149 accepted native fixes are committed locally across 150 tracked IDs; held ID 120 and two test-only repairs are excluded. [Every accepted fix and commit](../css-pow-special-value-acceptance-publisher-v2/readout/README.md).

| Area | Accepted fixes |
|---|---:|
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

| Investigation | Evidence and next step |
|---|---|
| Bloom milestones 1–6 | Complete within recorded bounded scope. |
| Installed Firefox 158 masked timing | Six controls PASS; three positive cases FAIL; four OK endings. Observation replayed; failed initial cleanup followed by verified root recovery. |
| Local original nine cases | Six PASS, three FAIL, four OK; original source/application state verified. |
| Unconditional one-line admission | Rejected: target repaired but two outline controls regress. Fully restored. |
| Snapshot candidate V1 | Enum declaration mismatch failed compilation. No browser execution; restoration and backup cleanup verified. |
| Corrected snapshot candidate V2 | Build 0, browser 0, nine PASS/four OK. Three improvements and six unchanged controls. Strict observer equality gate remains false; source/application restoration independently verified. No native acceptance. |
| Partial-base timing policy | Actual 24px: Firefox 1000ms/.75 vs Chrome 1500ms/.5. Literal records match; both raw/reference replays and cleanup pass. Candidate 24px and normative selection remain unresolved. |
| Duration-input variant | Five reviewed edits in manager cpp; uses the compared list for timing. Uncompiled/unexecuted; taint, serialization and policy obligations remain. |
| Preservation and taint fixtures | Two independent pages/three callbacks each, statically checked and reviewed; no browser results yet. |
| Verification cost | Manual benchmark with hash defaults, presets, raw timings and final-value checks; no measurements yet. |
| Descendant completion | Unresolved; previous candidates fail first reads at tested depths. |
| Formal snapshot lifecycle | 13 audited claims/six rejected false controls; explicit assumptions, no native refinement or canonical-count increase. |
| Min/max and logarithm fixes | Validated native/WPT payloads; pending research checkpoint and separate signed publication. |
| Research commits | V81 failed 1Password signing; fresh completed-work checkpoint preparation underway. |
| Untracked audit V9 | 563 expected paths: 68 exact project recovery matches; 495 unrelated metadata entries unchanged. Empty staging and held provider sole tracked edit after restoration. |

[Plan and remaining scope](PLAN.md). Build/test completion, historical strict comparison, restoration, and native acceptance are separate recorded outcomes.
