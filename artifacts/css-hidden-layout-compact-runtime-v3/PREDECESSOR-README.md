# Compact hidden-layout and column-observer experiment v2

**Source-only plan, not prepared or executed.** Do not invoke preparation until the full combined experiment has restored all sources, removed its six temporary tests, and root has finished signing completed research. No INPUTS or prepared source snapshots exist yet. V1 remains immutable; this additive successor is the proposed execution plan. The root alone runs preparation, builds, and browser tests.

## Six source variants

| Phase | Flex body | Absolute body |
|---|---|---|
| baseline | reviewed HEAD baseline | original |
| principal-only | principal subtree mark | original |
| oof-only | reviewed HEAD baseline | selected v2 pre-RI hidden OOF mark |
| both | principal subtree mark | selected v2 pre-RI hidden OOF mark |
| original-key | sealed v1 original-key flex | original |
| original-key-principal | sealed v1 original-key candidate flex | original |

The last pair reuses the exact sealed `css-hidden-geometry-wpt-runtime-v1/variants` bytes. Its original-key removes **both** the containing-block and border-padding key members, matching that predecessor; it is not mislabeled as a containing-block-only omission. Its principal variant differs by the same one-line hidden principal mark. All six phases explicitly reinstall both flex and absolute bodies, so the combined phase cannot contaminate either original-key run. Source-role origins and hashes are in DEPENDENCIES.json.

The other19 native write targets use captured post-signing HEAD bytes during the experiment. All21 native originals are restored byte-for-byte and rebuilt in `finally`; five more native guards remain untouched, for26 total. There is no timing hook, new preference, or repeat of the full686-regression corpus. Optional trace builds are described below.

## Exact test partition

Six files,58 subtests per phase:

- 12 original-key direct/leaf flex sizing cases;
- 8 fixed-size exposure/control cases;
- 18 principal placement, dirty-parent, and anonymous-text cases;
- 4 direct absolute cases;
- 8 absolute leaf-first cases;
- 8 new column/column-group queries and table/cell controls.

The first50 are exact copies of `css-hidden-layout-landing-plan-v1`; the last8 are from `css-hidden-table-column-query-v1`. CONFIG binds every ordered name and installed path. All58 raw outcomes remain diagnostic: unexpected failures are retained rather than stopped at the first failing test. Completeness requires six distinct harness-end records with status OK, exact unique subtest rosters, PASS/FAIL subtest statuses, and one suite_end. Process exits0/1 are retained. No blanket PASS requirement, expected-failure normalization, or new native-acceptance decision is encoded.

Column results require manual calibration/source adjudication. The original-key pair isolates the preexisting measurement route independently of the strengthened key. Neither source independence nor a passing combined variant alone establishes both fixes are landable separately.

## Preparation and execution gates

Preparation requires the combined runtime's STATE to be terminal/restored with successful restoration build and no recovery errors, and its BEFORE/FINAL snapshots to match. A prior diagnostic failure key (such as the timing cleanup permission error) is allowed only when all these restoration gates pass; it is retained as historical evidence, not recast as successful timing. The union of its six temporary test paths and this plan's six paths contains nine distinct destinations; **all nine must be absent, including dangling symlinks**. This rejects the overlapping currently installed fixtures instead of overwriting them.

After root signs, it supplies the actual post-signing HEAD explicitly:

```
python3 -I -S prepare.py --draft-sha REVIEWED_DRAFT_SHA --expected-head POST_SIGNING_HEAD
```

Preparation performs only read-only Git queries and artifact writes. It requires an empty index and verifies the two baseline HEAD bodies still equal the reviewed bodies. It captures all21 original/HEAD source roles,26 guards, current test/resource/metadata hashes (including absent metadata), and the prior terminal receipt hashes. A changed baseline is rejected; no candidate is silently rebased.

Root reviews emitted INPUTS and then may run:

```
python3 -I -S experiment.py --inputs-sha REVIEWED_INPUTS_SHA [--with-traces]
```

Execution reauthenticates prepared payloads/state/resources, installs its six tests with exclusive creation, lints them, replaces21 sources with captured HEAD, and performs six uninstrumented build/test phases followed by the two optional trace phases. It saves phase source hashes and per-WPT source/binary/resource snapshots. Each phase checks source and HEAD/index stability around build/test. Restoration removes only test paths actually created by this invocation, restores all21 original sources, rebuilds if any native write was attempted, and requires final native diff/source/HEAD/index snapshot equality and all nine temporary destinations absent. Error receipts are retained; restoration uses the predecessor's fallback logging/error accumulation pattern.

The copied WPT helper was narrowed only to require OK harness ends, since this compact roster contains no reftests. Preparation retains the predecessor-terminal/absence guard and adds the exact12-case trace-roster check. V2 adds only optional trace dispatch/receipt processing to the v1 execution script; it retains the two exact original-key roles and has no timing code. Per-script diffs against immutable compactv1 are retained for concise review.

## Optional causal traces

`--with-traces` appends two phases **after all six uninstrumented phases**:

| Trace phase | Flex | Absolute |
|---|---|---|
| trace-baseline | baseline | reviewed selected v2 baseline trace body |
| trace-oof-only | baseline | reviewed selected v2 OOF repair trace body |

Both trace phases explicitly reset flex to baseline. Each runs only `hidden-flex-absolute-geometry.html` (four direct cases) and `hidden-flex-oof-descendant-query.html` (eight leaf-first cases). No column, principal, extra regression, or timing workload is run under instrumentation. CONFIG binds the exact ordered12 names via the unchanged full roster.

The selected trace bodies are copied byte-for-byte from the reviewed combined-driver inputs. They record `[hidden-oof-before]`, `[hidden-oof-return]`, and `[hidden-oof-commit]`. Raw WPT logs remain intact; TRACE-LINES.json and stage counts are supplemental extraction only. All three stages must appear, but counts alone do not prove a clean-zero publication sequence or associate each native frame with a particular DOM target. That causal interpretation requires inspection of raw case/frame records.

Trace outcomes are stored separately under STATE.traces; they never replace or normalize the six uninstrumented results. Any exception still enters the same original21-source/test restoration and build path.

## Checks performed

Python AST parsing and Node callback registration were run without executing any DOM test callback or driver. Six exact ordered rosters total58. Both original-key source roles were authenticated against the sealed predecessor manifest; the compact/column HTML copies match their sealed producers. No live source snapshots, HEAD query, INPUTS creation, preparation, browser, build, native mutation, or Git operation was performed for this draft. A first assembly attempt used the wrong retained variant subpath and stopped before any driver existed; the corrected source lookup uses `variants/<role>/nsFlexContainerFrame.cpp`.
