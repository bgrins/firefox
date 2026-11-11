# Custom keyframe probe v2: execution and contract review

Independent raw-result and restoration review passes; the runtime hold is released. Root executed the diagnostic. This reviewer authored the wrapper and independently verifies the execution, rather than claiming independent wrapper authorship.

Execution HEAD: `ec467c0219d3d5daf70f42fcc53677cf8a262173`. Frozen manifest: `b71bb9e8150c7d4f33ef63c4acfd190d23b6d6750f4a9f967c2b8321056fc31b`. Lint and WPT exited 0; no native build ran. Raw JSONL has exactly seven PASS callbacks, one OK harness ending and eighteen unique observations. A separate lifecycle/inventory walk and the frozen full-schema parser agree with saved observations. No getter-value oracle was added to achieve this result.

| Scenario | Getter observation across all phases | Contract interpretation |
| --- | --- | --- |
| Original variable | Generated red custom/black color start, replace; authored green custom/green color end, auto; steps(2,start), offsets 0/1 | Custom membership is correct. Animated dependency context is green throughout; rendered half-green then green is a separate sampled quantity. Old inventory is stale. |
| Original custom-only | Empty custom value plus translate(100px) at start; 200px plus none at end; auto/ease, offsets 0/1 | Empty is guaranteed-invalid serialization, not absent membership. Old inventory is stale. Transform serialization need not equal getComputedStyle's resolved matrix. |
| Unregistered reference | Empty generated start; literal var(--source) authored endpoint | Source is 12px throughout; rendered stored value reaches 12px. CSS computed-value return requires substitution; this is a getter discrepancy. |
| Registered relative, replace | Generated typed length/marginLeft 10px; authored typed length, marginLeft and unregistered token all 2em | Font is 16px; current typed/ordinary values are 10/15.5/26.5px. CSS endpoint computation should return 32px for typed/ordinary lengths. Unregistered 2em is correctly a token value. |
| Registered relative, add | Same strings; generated composite add, authored auto; effect add | Current typed/ordinary values are 10/18/34px. The same computed endpoint discrepancy persists. This does not prove roundtrip recreation of implicit additive frames preserves composition. |
| WAAPI specified control | One authored frame, null offset/computedOffset 1, auto/linear; all three strings 2em | Plain Animation takes the specified-value branch. These values are appropriate even though current typed/ordinary values render in px. A fix must preserve this branch. |

All CSS returned arrays, memberships and metadata are stable across this capture. Current times are 0/25000/75000 and progress 0/.25/.75. That is not a general phase-invariance claim: element dependency changes can change computed keyframes.

The current [getKeyframes branch](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes), [computed-keyframe calculation](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes), [dependency context](https://drafts.csswg.org/web-animations-1/#computing-property-values), and [registered computed-value rule](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time) are traced and captured in `css-keyframe-custom-property-contract-20261110-v1`. Applied here, they support a getter serialization defect spanning ordinary relative values, registered relative values and custom substitution. Investigate the shared return path; do not count three bugs or infer rendering failure. Bug 1391537 is historical context, not an established duplicate.

Restoration independently verifies 9,378 application entries, three extras, retained seven source/test paths, binaries, configuration, test/profile pins, absent temporary fixture/metadata, HEAD and logical index. Tracked source/index are clean. Owned groups, backups and lock are absent. REVIEW.json records PASS. Full logs retain familiar nonfatal SWGL framebuffer and unsynced Nimbus diagnostics, with no harness crash, timeout or lost result.

JS reads are sequential, not an atomic engine snapshot. Paused explicit seeks and static font/source context support these bounded conclusions; this does not prove general provider coherence. No production patch, WPT oracle edit, catalogue increment or final missing-pseudo/debug acceptance is made here.
