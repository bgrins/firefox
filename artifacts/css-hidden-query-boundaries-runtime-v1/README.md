# Hidden-query boundary experiment draft

Source-only controller; not prepared or executed. Root authorizes execution only after controller review. Proposed starting HEAD is `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`; `prepare.py --expected-head` authenticates the supplied current HEAD. Historical predecessor restoration is authenticated against its own BEFORE/FINAL, not the new HEAD.

## Phases and scope

Each phase runs 104 tests in nine files: prior66, compact18, provider20. The five committed landing files (50 cases) are read and pinned, never installed or removed. Four diagnostic files (54 cases) must initially be absent, are exclusively created, then removed in restoration.

1. baseline: accepted principal104 and absolute105, neither new candidate.
2. column-provider: baseline plus the column provider gate.
3. skipped-line-block: baseline plus marking every skipped line child.
4. both: both new candidates.
5. standalone-baseline: remove exactly104 and105; keep the containing-block measuring key101.
6. standalone-column-provider: standalone baseline plus column gate.
7. standalone-skipped-line-block: standalone baseline plus skipped-line marking.

The four main phases require exact identity/status/message and file-end agreement with their prior66 historical counterparts. Standalone baseline requires the older30PASS/36FAIL oracle, after exact28source and old-resource equality checks. There is no historical oracle for the two standalone single-candidate phases. New38 outcomes are diagnostic; no forced expected status. Separate tracked50 and candidate54 counts prevent interpreting removed104/105 failures as regressions in the new candidates. Independence comparisons use the standalone baseline and relevant candidate cases; this is not a clean upstream build of every other pending change.

A failed assertion explicitly labeled calibration (or the older independently constructed visible-reference label) stops after retaining raw RUN, then restores. It may reveal an invalid fixture/support assumption or a real native regression; do not automatically attribute it to the fixture. Ordinary geometry failures remain evidence and permit later phases. Visible span/fragment calibration is mandatory. Content-visibility:auto scrolling remains outside this roster.

## Cost runs

Only baseline and both execute the original closed `css-hidden-query-cost-v1` capsule directly, with its external FILES pin. No copied launcher or changed config. All28native sources, Firefox/XUL and six execution inputs must join the immediately preceding phase WPT and remain unchanged. Parent revalidates exact220progress,90rows,2,952,000reads, startup environment and cleanup/profile termination. Geometry mismatch counts are allowed evidence; calibration, runner, integrity or cleanup failure stops and restores while preserving WPT receipts. These are one process per variant in fixed order; no broad no-regression or statistical conclusion follows. No cost runs occur in the other five phases.

## Restoration and preparation

The reviewed predecessor mechanics remain: authenticate draft and external dependencies, capture23 original working-source files and exact HEAD alternatives, normalize those23 to HEAD during phases, apply four selected role files, and finally restore every original byte and rebuild. All28source guards, HEAD/index, tracked tests, resources/metadata and temporary absence must agree with initial state. No source preparation or execution was performed by the author.

`python3 -I -S prepare.py --draft-sha DRAFT_SHA --expected-head APPROVED_HEAD` creates INPUTS only after exact source, test ownership and predecessor-restoration gates. Root then runs `python3 -I -S experiment.py --inputs-sha INPUTS_SHA`. No Git mutation occurs in either controller; Git reads authenticate HEAD/index and source roles.

The DRAFT manifest freezes controller inputs. INPUTS later additionally freezes source snapshots, resource/metadata pins, historical terminal receipts and the entire external cost capsule. `evidence/*.diff` records the three controller changes from the prior guarded runtime. Exact104/105 removal diffs and all five prior RUN oracles are retained. Static checks validate Python syntax, calibration-label discrimination, closed cost inputs and exact54 temporary test registrations; browser geometry and runtime behavior remain untested here.
