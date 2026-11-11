# Independent transient recascade v4 terminal review

The completed optimized experiment supports bounded acceptance of the request-local maps-to-style helper. The real binaries build, four installed lint commands, query driver and recascade driver succeeded. All 130 ordinary WPT records exactly match the retained baseline, including messages and expected classifications. This is not acceptance of a public missing-pseudo CSSOM repair or a debug-build gate.

## Raw execution evidence

Independent parsers read the original JSONL logs, enforce unique ordered callbacks and complete suite/test lifecycle, and reject unexpected callbacks, crashes and error-level records. They also compare each observation to the saved structured result rather than accepting its summary alone.

| Suite | Assertions | Tasks/pages | Result |
| --- | ---: | ---: | --- |
| Existing request-local query driver | 208 | 13 tasks | All PASS; 20 setup checks pass |
| New transient recascade driver | 100 | 6 tasks | All PASS; 6 setup checks pass |
| Ordinary WPT preservation | 118 plus 12 harness endings | 12 pages | 99 PASS, 19 retained FAIL, 12 OK; exact unchanged vector |

Both direct harnesses ended PASS and both Mochitest commands exited zero. Their 308 assertions include every required case; no skipped or unwitnessed later task is counted. WPT exits one for the retained failures; the independent comparison confirms no new status, inventory, message or classification change.

The v3 scroll-geometry failure remains preserved. V4 changes only the unnecessary horizontal scrollbar in that existing query fixture. All previously failed finite-timeline/named-range setup and result assertions now pass without changed expected values. Native candidate bytes and the 208/100 assertion inventories were preserved.

## What the result establishes

The direct recascade cases exercise caller-supplied separate origin maps, important-author precedence, overlapping/disjoint properties, removal of stale origin rules with empty maps, inherited and authored relative values, custom-property providers, logical mapping, eager pseudo layout-parent behavior through display:contents, After and permitted Marker values, and rejection of wrong identities or generated pseudos. The direct fixtures verify their required authored/donor/generated-pseudo setup before interpreting outcomes. Their observed original-style identity, pseudo identity and no-publication checks pass.

These are maps-in/style-out tests. Their overlapping maps deliberately test cascade behavior; they do not settle which map a real effect stack should select. The separate combined composer/recascade diagnostic and its three interpretation probes have not run in this experiment. Null-progress origin membership remains unresolved. Nor does this prove arbitrary reentrant safety, complete renderer neutrality, provider/endpoint coherence for a public query, visited-style privacy, caching or general lifecycle correctness. Marker uses the existing lazy-pseudo route and retains its documented layout-parent limitation; the passing Marker font case does not establish new display:contents behavior for Marker.

## Provenance and restoration

The review authenticates frozen RUN-INPUTS 2fa2939357b708381b7ad1b2f2fa8e816ef5faa5d9d2ee7e4568e001bf3370ff, all candidate source hashes, configuration and sampled binaries. The actual command is mach build binaries -j6. BUILD-LOG-SUMMARY.json records one SWGL compiler-option warning and four nonfatal build-monitor KeyError export tracebacks; no compiler errors were found, and the build exited zero. These diagnostics are retained rather than silently omitted.

The independent live scan verified all 9,378 app entries, 42,811 installed Mochitest entries, six extras, all 14 source roles, original test/config files, HEAD/index and all 527 unrelated untracked path identities. Temporary fixtures, owned backup directories and transaction lock are absent. All ten command process groups are absent from a fresh independent process snapshot. Root was explicitly released for subsequent Git/native/app work after these checks passed.

This review is independent execution/result and restoration verification. The reviewer prepared the fixture-only v4 wrapper amendment; root separately reviewed and froze it before execution. It is not claimed as independent authorship review of that amendment. No live source, browser or Git mutations were performed by this terminal review.

The next integration step may use this accepted helper prerequisite. Public CSSOM orchestration and its final debug transform/change-hint gate remain outstanding; the candidate was restored rather than landed.
