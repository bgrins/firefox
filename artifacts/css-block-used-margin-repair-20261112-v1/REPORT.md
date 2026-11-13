# Refresh used margins for overflowing blocks

ReflowInput::CalculateBlockSideMargins returns early when a block's content
and initial margins exceed the available inline size. It adjusts the reflow
state's inline-end margin but leaves an existing UsedMarginProperty unchanged.
getComputedStyle therefore exposes zero or the unresolved percentage-derived
end margin instead of the value used by layout.

The three-line native change refreshes that existing property before returning,
using the containing block's writing mode just as the successful-space branch
already does. It creates no new frame property and changes no allocation or
layout-position calculation. The standalone candidate.patch contains only
ReflowInput.cpp and resolved-margins-overconstrained-block.html.

## Evidence

- Baseline: 96 WPT subtests, 30 pass and 66 fail. Both directions, horizontal
  and both vertical writing modes, three sizes, four margin forms, and repeated
  fitting/overflowing transitions are covered. Expected values are an explicit
  table derived from the block-width equation. Baseline sequence tests stop at
  their first failing overflow; the repaired runs execute every transition.
- Native build: mach build binaries -j2 exits zero with zero compiler warnings.
- Rebuilt browser: all 96 regression subtests pass. Existing computed-style-005
  and cssom-getBoxQuads-001 also pass, totaling 106 subtests across three files.
- WPT lint and clang-format lint report zero errors and zero warnings. The
  obsolete mach clang-format command attempts are retained as failures, not
  formatting evidence. git diff --check passes.
- verify.py validates source/test pins, identical baseline/fixed case names,
  exact outcome counts, binary continuity, and fresh absence of every owned
  command group. The two-file patch applies and reverses exactly in disposable
  scratch, which is removed afterward.

Each main wrapper encountered PermissionError during final process-group
inspection after its mach child had terminated. Original COMMANDS.json,
CLEANUP.json and driver failures remain unchanged. Independent follow-up
checks confirmed those groups absent; ACCEPTANCE.json records the recovered
evidence. The native build also retained the previously encountered nonfatal
build-monitor KeyError for the export tier. Neither issue is hidden by a retry
of the build or test commands.

## Scope and disposition

This is a source/spec audit finding and historical rediscovery of the remaining
negative-space case from bug 381328, closed as a duplicate of bug 1298008. It
adds one locally validated repair candidate, not a novel vulnerability or a
universal native proof. See ../css-block-used-margin-audit-20261112-v1/SPEC-TRACE.md.

Literal-length-only margins still follow the existing fast reporting path;
the broader compatibility question around those values is not solved here.
The new test covers auto/percentage margins whose values are already tracked.
No cross-engine runtime test or whole-layout regression claim is made.

Independent source/spec/report review found no blocker; see
../css-block-used-margin-independent-review-20261112-v1/REPORT.md. Root
authenticated its 17 frozen files and 19 reviewed inputs. That reviewer did
not rebuild or rerun the browser. Orthogonal child/parent writing modes and
property removal/recreation are useful follow-up coverage, not claims made
by this matrix.

Suggested relative triage priority is P3: incorrect CSSOM/geometry observations
can affect measuring scripts and developer tools, but this evidence shows no
memory-safety issue or changed layout-position calculation.

The change is applied and built locally, pending a signed commit. Signing has
not been retried or bypassed. Suggested subject: Refresh
used margins for overconstrained blocks. Research/tooling belongs in a preceding
commit; candidate.patch is the independent native-plus-WPT change.

The new runtime authority is build/after-BINARIES.json. Previously frozen exact
reflow migration candidates predate this cache repair; their successors must
compose it explicitly rather than overwrite the live source from old copies.
