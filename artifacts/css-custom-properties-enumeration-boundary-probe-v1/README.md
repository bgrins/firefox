# Custom-property count and iterator boundary

Local shared-tree experiment, 19 October 2026. No native repair is accepted or
committed by this artifact. Discovery came from source review and browser
execution while developing the map proofs; Lean did not discover these cases.

## Browser results

Seven WPT files completed with 39 subtests and seven OK harness results in each
variant. `check-results.py` authenticates the source snapshots and binary
associations, compares the exact test identities and stable neighboring inputs,
and writes `OBSERVATIONS.json` with full failure messages.

| Variant | PASS | FAIL |
| --- | ---: | ---: |
| Original | 30 | 9 |
| Iterator label only | 33 | 6 |
| Live count and indexed filtering only | 36 | 3 |
| Both repairs | 39 | 0 |

The count repair fixes five flat guaranteed-invalid enumeration failures. It
also passes the restored-name chain in this observed iteration order; the two
calibrated shadowing failures and present-name chain still expose the original
duplicate iterator. This passing restored-name case does not prove raw iterator
correctness. The combined repair passes every case.

The iterator-only variant exposes a concrete count inconsistency: a restored
name produces 17 real names plus a literal `--`, with reported count 18. The
original produces duplicate names instead. The source explains the indexing
hazard, but this experiment did not run a debug build or reproduce a panic.

## Source changes

`count-fix.patch` compares effective value presence before mutation with the new
Option value, adjusts the count on presence changes, and filters removed entries
in indexed access. It preserves raw tombstones, which must shadow ancestors.
Valid empty values remain Some and remain enumerable.

`iterator-after-count.patch` targets the outer loop when an ancestor name was
already owned by a descendant. Its original label-only form must not be offered
as an independently safe upstream patch after the count interaction was found.
The main stack can place the count repair first; a standalone iterator alternative
must include that necessary support, with the dependency recorded in the ledger.

## Evidence limits and next gates

The original source equaled HEAD, so `run.py`'s dirty-file roster omitted that
native file from its before/after-test pins. The build driver checked its exact
source after compilation and before WPT; the original run has no explicit
after-test map pin. This is a retained diagnostic comparison, not the final
acceptance pair. The next runner must name the native path explicitly, including
when it is clean against HEAD.

The iterator-only build association comes from the completed preceding
`css-custom-properties-map-iterator-fix-v1` pair. The other three builds are
recorded in `BUILD-MATRIX.json`. All builds returned zero and completed linking;
each also emitted four preexisting build-monitor `KeyError: 'export'` diagnostics.
Full logs are retained. None of these runs is an isolated-upstream build.

Next add last-value removal and inherited/non-inherited indexing boundary cases,
rerun the final pair with complete explicit pins, finish the source-shaped Lean
count and iterator obligations, obtain independent acceptance, format/lint the
scoped patch and create separate evidence/native commits. The committed native
fix count remains 73.

CSSOM excludes guaranteed-invalid computed custom properties from enumeration:
[getComputedStyle](https://drafts.csswg.org/cssom/#dom-window-getcomputedstyle).
The valid-empty distinction is specified by
[CSS Variables](https://drafts.csswg.org/css-variables/#guaranteed-invalid-value).
Related historical [bug 1855629](https://bugzilla.mozilla.org/show_bug.cgi?id=1855629)
introduced registered-property enumeration and was resolved for Firefox 120;
this investigation does not claim exhaustive duplicate-bug clearance.
