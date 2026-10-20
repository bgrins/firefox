# Traversal v4 browser comparison

**Correctness passes; independent runtime/performance review pending.** No native
repair is accepted by this experiment. Six fresh headless processes and three
successful builds completed. Original source and build are restored; the staged
research commit contents, stage entries and HEAD are unchanged through the final
timing process. The four temporary candidate source files and WPT are no longer
installed. Other native prototypes and DOMRect fix 102 were preserved.

## Browser correctness

The 23-file, 74-subtest comparison changes 70 PASS / 4 FAIL into 72 PASS / 2 expected
FAIL. Only the horizontal and vertical 139808.125px untransformed-edge cases change
from FAIL to PASS. All four new WPT cases pass; the other 70 subtest outcomes and
all 23 file outcomes are unchanged. The two existing expected failures are SVG
rotated-text Element/Range equivalence and trailing-surrogate Range indexing.

The baseline is compared to retained DOM-only calibration. DOMRect fix 102 is
captured in both phases, so this is not a v4-without-102 or isolated upstream run.
Source packaging establishes applicability separately, not runtime independence.

WPT lint and warning-as-error clang-format checks pass. Baseline/candidate/restore
build exit codes are all zero. The Mach progress monitor still emits its existing
KeyError for export; underlying builds explicitly succeed. Build summaries report
zero warnings for the incremental baseline and 21 for each full candidate/restore
build. BUILD-OBSERVATIONS retains the extracted warning lines and summaries; equal
counts alone are not a full warning-category equivalence check.

## Timings

Each process runs six topologies, with 11 rotating batches of 100000 calls and
10000 warmup calls per topology. All geometry, checksums, order, visibility,
source and binary stability checks pass. Totals are 396 batches and 39.6 million
measured calls. Batch durations range from 11 to 51 ms. Integer-millisecond timer
values correspond to 10 ns/call increments at this batch size.

Process medians in ns/call:

| Case | Before | Candidate | Restored |
| --- | --- | --- | --- |
| ordinary-128 | 310, 320 | 330, 310 | 330, 320 |
| ordinary-8 | 140, 150 | 130, 120 | 140, 160 |
| transform-near-leaf-128 | 370, 360 | 340, 340 | 360, 350 |
| transform-near-leaf-8 | 190, 200 | 190, 190 | 200, 190 |
| transform-near-root-128 | 380, 360 | 380, 390 | 380, 370 |
| transform-near-root-8 | 200, 190 | 200, 190 | 200, 190 |

The tested ordinary deep path matches the baseline range, and deep leaf-transform
medians are lower than all four baseline medians. Deep root-transform medians are
380 and 390 versus surrounding 360–380; the descriptive phase-center difference
is 10 ns/call (about 2.7%). One candidate median overlaps the baseline maximum;
the other is one timer increment higher. Preserve this residual concern for
independent review. These data do not prove significance, general regression,
no regression, or a broad speedup. Fixed phase order, only two processes per phase,
local drift and rebuilt binaries limit attribution. V3 is historical context,
not a paired comparison to v4.

## Integrity and restoration

INPUTS binds 378 files, HEAD and the exact staged diff/full stage-entry hashes.
BEFORE and FINAL agree on HEAD, both index hashes, four original source hashes and
all fixed native hashes; FINAL additionally confirms temporary WPT absence.
This preserves staged content, modes and stages, not raw physical index metadata
or flags. No commit/index mutation was performed. Original baseline and restored
binaries need not be byte-identical; their contemporaneous hashes are retained.
Historical binaries are not archived or rebuilt by the offline verifier.

The live-input analyzer passes and retained-input analysis reproduces the same
performance comparison. Non-artifact input snapshots are captured; immutable
artifact dependencies remain siblings referenced by INPUTS. This is not a claim
of a single-directory relocatable runtime artifact. All six temporary browser
profiles were removed. The active objdir remains available.

The first offline WPT summary assumed matching expected failures always included
an explicit expected field. WPT omits that field; the corrected summary uses
expected-or-status normalization. The initial script/failure and explanation are
retained under development. Browser results and the executed experiment driver
were not changed to repair this postprocessing error.

Full native provider, heap/lifetime and safe-origin obligations remain open.
