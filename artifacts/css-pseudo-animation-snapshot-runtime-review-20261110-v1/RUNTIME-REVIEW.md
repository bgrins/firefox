# Completed optimized snapshot experiment

The completed experiment supports bounded local acceptance of the owned-input
prerequisite refactor. The native candidate built successfully; all 125 distinct
assertion/harness records were preserved; the complete original application,
sources and extras were restored. This does not accept or count a missing-pseudo
fix, and does not close its separate debug or freshness gates.

This terminal review supplements the unchanged preparation `REPORT.md`.
Evidence is `css-pseudo-animation-snapshot-runtime-20261110-v1/baseline1`
and `candidate1`, under frozen inputs
`1eee630c4c76f63f09efb454bbf6fa84bca20103e7c822ac968d293db7352c23`.
`RUNTIME-CHECK.json` pins both raw logs and the source/build/restoration receipts.
The reviewed native patch remains
`b37e4885614c5b2acb7fa4320ca734fd2c7fa1062e12f5b55c6e60be71d25166`.

## Independent results

The review-owned parser independently read both raw traces without importing
the runtime analyzer. It required exact page identity, paired lifecycles,
distinct assertion/harness identities, no duplicates, successful harness ends,
valid assertion counts, and no crash or structured ERROR/CRITICAL log. Both
variants have 114 callbacks (94 PASS, 20 FAIL) plus 11 OK harness endings.
Every identity and status matches, and the independent reduction equals the
saved parsed receipts. There were no structured warning events in either run.

| Coverage group | PASS | FAIL |
| --- | ---: | ---: |
| Retained pseudo CSSOM lifetime fixture | 13 | 7 |
| Pseudo underlying/base fixture | 6 | 3 |
| Target/pseudo assignment | 17 | 7 |
| CSS `getKeyframes` | 29 | 3 |
| CSS `setKeyframes` | 3 | 0 |
| CSS animation effect replacement | 8 | 0 |
| Four named-range pages | 6 | 0 |
| Keyframe attribute mutation | 12 | 0 |

The target failures include six nonexistent-pseudo cases and one unsupported
`::placeHOLDER` case. They are not all attributed to one CSSOM bug. The three
CSS `getKeyframes` failures concern same-time frames with different easing/
composite, a variable overridden by a keyframe value, and a custom-property-only
keyframe. All 20 failures are retained baseline outcomes, not improvements or
new regressions. The 12 attribute and six range cases actually reached passing
assertions, avoiding a preservation claim based only on unsupported failures.

The wrapper compares statuses and identities, not message strings. This
review additionally compared the `message` field for every matched assertion
and harness record and found zero differences. That finite observation still
does not prove equality of every internal value or behavior outside the tested
assertions. Full raw and text logs remain the evidence.

## Build and restoration

The candidate build exited zero, compiled the affected animation dependents,
linked `toolkit/library/build/XUL`, and reported success. Its receipt records
the exact candidate source/config hashes. Build binary samples match the
test samples and differ from baseline; the runner checked them again after
testing. Both WPT command outcomes passed the strict parsing/preservation gate;
the known callback failures were retained rather than suppressed by metadata.

The build log is not diagnostic-free: it contains four nonfatal Python
stdout-monitor tracebacks from tier begin/finish bookkeeping, each ending in
`KeyError: 'export'`. The compiler/link process still completed with exit zero
and the produced binary passed the runtime comparison. These diagnostics do
not identify a snapshot source or linker failure. `RUNTIME-LOG-SCAN.json`
records them alongside the full build-log hash. This review does not silently
equate command success with an empty diagnostic log.

Only after terminal `RESULT.json` reported successful restoration did the
reviewer inspect live files. Independent checks verified:

- All 9,378 original application entries by path/type/mode and file hash/size or
  symlink target, plus all three explicit build/test extras.
- Both original native source hashes, all retained clip-fix-171 binary samples,
  mozconfig, the 34 test/metadata pins and absent temporary fixtures.
- Execution HEAD, Git index fingerprint, and empty tracked/staged diffs.
- Removed owned backups and runtime lock, and no non-zombie members of the
  three owned process groups, 57044, 57569 and 60574.

The first reviewer process inspection was blocked by the sandbox's `ps`
restriction; an approved read-only rerun completed all checks. No source,
browser or Git mutation was performed by this reviewer. Root was notified
when live verification finished so the exclusive hold could be released.
Build intermediate objects are not claimed to have been rolled back.

## Remaining limits

This is optimized ordinary-path preservation, with no CSSOM hook, new pseudo
traversal or new bugfix. The captured pseudo request intentionally remains paired
with its captured target under hypothetical reentry; this experiment is not a
universal equivalence proof for arbitrary reentrant mutation. Shared declaration
blocks are not deep immutable snapshots.

Named-range offset refresh followed by correct CSS regeneration, provider/base
context, selected cascade masks, timing coherence, lazy-resolution recursion and
explicit revalidation remain future integration obligations. The final
missing-pseudo debug gate remains open. These passing tests do not waive it.
