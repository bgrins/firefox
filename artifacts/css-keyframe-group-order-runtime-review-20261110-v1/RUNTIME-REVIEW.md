# Completed runtime review

The bounded optimized experiment supports accepting the percentage-keyframe group-order repair for known bug 1778402. Both runs completed, the two intended callbacks improved, all other statuses/messages matched, and the complete recorded application/source state was restored. This is independent verification of root's runtime evidence; the reviewer authored the native candidate and does not claim independent native authorship review.

Inputs remain bound to manifest SHA256 `e9eb714152ef47eb67ab604acc4f207ed151428b3c3bc46ae40255d28c215317` and execution HEAD `a4ead15121655260247a504eef4aae28ae6c22b1`. The final executable inputs were reauthenticated after the runs; none changed. `RUNTIME-INPUTS.json` authenticates the result/log receipts examined here.

| Independent raw reconstruction | Baseline | Candidate |
|---|---:|---:|
| PASS callbacks | 75 | 77 |
| FAIL callbacks | 11 | 9 |
| OK harness endings | 9 | 9 |
| Total kind-tagged records | 95 | 95 |
| Attribute-dependency controls | 12 PASS | 12 PASS |
| Named-range controls | 6 PASS | 6 PASS |

Only these assertions changed from FAIL to PASS:

1. The existing same-offset/different-easing-and-composition case, strengthened to require the later 10px margin declaration within the earliest-position group.
2. The new interleaved-offset case, requiring earliest group order and a later logical declaration's 30px physical margin value.

The new baseline failure is specifically a frame-1 property-order mismatch: expected `marginLeft`, received `marginRight`. Candidate PASS reaches the full frame-list oracle, including all values, offsets, easing and composites. The original case also reaches its strengthened full oracle. All 93 remaining records retain identical statuses and messages. The nine retained failures are the existing seven target/pseudo cases and two custom-property inventory cases; they were neither hidden nor reclassified.

`runtime-review.py` independently parsed the raw JSONL streams without calling root's analyzer. It rejected duplicate records/JSON keys, required complete lifecycle, reconstructed the exact callback inventory, distinguished assertion and harness keys, compared actual statuses and messages, and checked the intended changes against the frozen list. Both WPT commands exited 1 for the anticipated metadata situation: the baseline's new failure has no annotation, and the candidate's original case is still annotated FAIL during the experiment. Both runner transactions exited successfully; these WPT process codes did not bypass the record-level gates.

The candidate performed the real optimized `mach build binaries -j6` and exited 0. Build receipt hashes match all three candidate source-role files and the sampled binary receipt; the sampled application differs from the retained baseline. WPT lint exited 0 with no problems. The build log contains four preexisting-style build-monitor `KeyError: 'export'` tracebacks in tier accounting, followed by successful completion and zero compiler warnings. They are preserved as nonfatal diagnostics, not silently described as an entirely clean log. Both WPT logs show the same headless SWGL framebuffer diagnostic and empty Nimbus database messages; neither raw stream contains a crash event or ERROR/CRITICAL harness record. See `LOG-REVIEW.json` and the full original logs.

After root's terminal notification, a fresh scan verified all 9,378 application entries against the pre-run map, plus three build extras. Native and WPT sources, all test pins/metadata-presence checks, retained binary hashes, mozconfig, HEAD and index matched their originals. Baseline and candidate pre-run application maps were semantically identical. Both backup directories and the runtime lock were absent. Fresh process-table inspection confirmed absence of all owned build/lint/test groups. The first sandboxed audit reached the final process-table check and was denied access to `ps`; a read-only escalated rerun passed the entire audit. Root was notified immediately when the live audit finished so the execution hold could be released.

This supports the narrow grouping repair and exact approved delivery patch. It does not demonstrate broad performance equivalence, debug-build coverage, arbitrary future caller safety, or a complete implementation of CSS keyframe semantics. The separate missing-pseudo CSSOM repair remains unresolved. The abstract Lean order proof and source ownership/declaration audit retain the scope limits documented in the candidate capsule.
