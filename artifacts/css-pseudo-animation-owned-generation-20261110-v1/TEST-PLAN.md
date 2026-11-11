# Bounded preservation experiment

Use `TEST-INVENTORY.json` (eleven pages), whose current test scripts and metadata presence are pinned in `TEST-SOURCES.json`. The two retained temporary fixtures are copied from tracked prior research inputs. Do not install them or the candidate until a separate reversible runtime wrapper is reviewed.

| Page or group | Relevant path |
| --- | --- |
| retained `pseudo-compose-cssom-lifetime.html` (20 cases) and `pseudo-compose-underlying.html` (9) | Generated/missing pseudo, underlying values, lifecycle and retarget controls; existing missing-pseudo failures must remain visible. |
| `KeyframeEffect/target.html` | Normal effect target changes and missing/generated pseudo behavior. |
| CSS `KeyframeEffect-getKeyframes.tentative.html` | CSS virtual-default capture, implicit endpoints, easing/composite grouping and defaults, percentage ordering; includes current #172 changes. |
| CSS `KeyframeEffect-setKeyframes.tentative.html` | JS replacement of CSS keyframes and generation opt-out. |
| `CSSAnimation-effect.tentative.html` | Effect replacement/detachment and CSS/default generation behavior. |
| `merge-timeline-offset-keyframes.html` | Percentage/range combination and equal-offset generation; preserve current observations, including any separately identified stale expectation. |
| `timeline-offset-in-keyframe-change-timeline.tentative.html` | Existing live timeline change and CSS endpoint regeneration. |
| `timeline-offset-keyframes-with-document-timeline.html` | Unresolved named-range offsets on an unsuitable timeline. |
| `timeline-offset-keyframes-zero-length-attachment-range.html` | Existing zero-range/unresolved handling. |
| `keyframe-attribute-mutation.html` (12 cases) | Preservation of the forwarded attribute-dependency output and dynamic property rebuild. |

Take a fresh baseline from the retained current-source browser, then install only this four-file candidate and run a real `./mach build binaries -j6` before the same tests. Pin actual HEAD/source/config/app hashes at wrapper freeze; do not assume an earlier snapshot experiment's counts. Current #172 and any subsequent accepted named-range changes require matching source/test/browser provenance. Do not change metadata to make this preservation experiment green.

Require exact record-kind/test/subtest/occurrence identities with duplicate rejection, all harness endings, expected classifications, and unchanged callback statuses/messages, allowing no intended behavior changes. Record build and harness exit codes, crashes, process termination and restoration receipts; compare the full application, extras, native sources, and absent temporary fixtures after both modes. Preserve raw logs, including unrelated expected failures.

These pages exercise the shared generator, CSS capture/opt-out, ordinary range management, attribute output, and retained pseudo paths. They **do not directly exercise the new explicit `PropertyInputSnapshot::RefreshComputedOffsets` API**, which has no production caller in this prerequisite. The source checker establishes delegation/order/no cached completed output only. A future query caller needs direct coverage showing changed named-range context refreshes its owned array before generation while renderer arrays remain untouched; no browser assertion is fabricated for an inaccessible internal seam here.

A successful optimized preservation run would support this bounded refactor only. The final CSSOM missing-pseudo hook still needs the separate debug gate and coherent timing/provider/masks/cache coverage described in the design report.
