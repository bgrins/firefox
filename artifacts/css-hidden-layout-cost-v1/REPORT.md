# Hidden layout cost diagnostic

Status: prepared and syntax/synthetic checked; **not browser-run and no performance result**. Intended for the four uninstrumented baseline, principal-only, OOF-only, and combined phases. This is a local diagnostic, not a conformance test or a claim that either repair is cost-neutral.

## Invocation and receipts

```
python3 -I -S /absolute/path/run.py --binary /absolute/path/firefox \
  --output /absolute/absent/output --label baseline \
  --pin /absolute/native/source --pin /absolute/resource
```

Repeat `--pin` for the enclosing experiment's fixed source/resource inputs. The runner automatically hashes its five execution inputs, Firefox executable, and adjacent macOS XUL before and after. It uses one fresh profile, no preference overrides, and an ephemeral loopback server serving only the three fixture resources. `RESULT.json` retains all raw observations and pins; `SUMMARY.json` reconstructs ordered batches/work checksums and descriptive distributions. `browser.log` and `BEFORE.json` survive failures. No external fixture resources or collectors are used; browser default background services are not disabled.

The browser starts in its own process group. The runner terminates that group, applies a bounded kill/reap fallback, closes the local server, and removes its owned profile before accepting a receipt. It never searches for or kills another Firefox process. A 75-second browser deadline produces a failed diagnostic receipt. Cleanup errors are explicit. Parent orchestration must abort on input/binary/resource drift or failed cleanup; a stable calibration/timeout failure can be recorded while continuing the remaining correctness phases. There is no detached timing job. This POSIX runner is intended for the current macOS workspace.

## Exact workload

Twelve configurations: principal versus absolute-positioned children; visible versus hidden parent; 1, 32, or 256 children. Each child has three nested 100%-size descendants. The selected leaf indices are `[0]`, `[0,10,20,31]`, or `[0,85,170,255]`. All branches are 8×8 CSS pixels. The flex parent is 160×64, alternated with 168×64. Absolute children use centered static positions, so width changes request updated hypothetical positions. This exercises the intended OOF path; this artifact does not instrument or prove the native dispatch count.

Two full warmup rounds are discarded, then seven measured rounds retain all twelve configurations, rotated by one slot per round. Each batch has sixteen mutation/flush iterations and sixteen recovery-preparation/query iterations. Totals: **84 measured batches, 1,344 mutation flushes, 1,344 recovery preparations, and 4,032 leaf geometry reads**. Warmups perform the same work but are not included in these counts or distributions. No adaptive sample removal or outlier filtering is performed.

Timers are milliseconds from `performance.now()`:

| Field | Included work |
|---|---|
| `constructionMs` | JS node creation, nesting, and connection; no deliberate geometry flush |
| `establishMs` | initial visible layout and exact 8×8/160×64 calibration, followed by entering the requested hidden state and outer flush |
| `mutationFlushMs` | sixteen width toggles plus outer geometry queries, without descendant recovery queries |
| `recoveryPrepareMs` | sum of sixteen width-toggle/outer-flush intervals |
| `recoveryQueryMs` | sum of sixteen selected-leaf geometry-query intervals |

The hidden mutation phase can expose extra dirty propagation on many skipped principal descendants or OOF trees. The recovery phase measures query-driven recovery separately. Visible configurations supply paired ordinary-layout controls, particularly selected absolute reflow overhead. Construction, initialization, mutations, and recovery remain separate; do not add them and call the sum a per-reflow cost. DOM removal and one event-loop yield per round are outside retained timers. JS, DOMRect allocation, scheduling, and garbage collection can contribute to the measured intervals.

## Calibration and interpretation

Visible calibration is mandatory before hiding each fixture. Outer-size/work checksums, exact row order and selected indices, geometry checksum, and read counts are validated. Hidden or visible recovery mismatches are retained as data, not converted into a timing failure or silently dropped. A faster result with stale/zero geometry is not equivalent completed work. The paired WPT suite remains the correctness gate.

Each group retains all seven samples, median, min, max, and zero-sample count for every timer. Sixteen iterations reduce but do not remove quantization. In particular, sums of short recovery intervals can contain multiple rounded zeros; equal/zero timings cannot establish zero predicate-lookup overhead. There is no subtraction of an empty-loop estimate and no significance/no-regression conclusion.

The fixture checks a 45-second deadline between batches; the runner's 75-second deadline bounds a stuck/slow browser. The expected goal is less than a minute per phase, **not yet measured or guaranteed**. Startup waits one second outside timers. Source/resource hashing and shutdown lie outside JS timers and can extend runner wall time. The parent should retain a timeout rather than reduce the sample roster after seeing results.

One fresh process per phase and fixed phase order remain vulnerable to machine drift, build aftermath, background activity, CPU state, and process-level variance. The rotating configuration order reduces within-process position bias only. A concrete cost signal can justify a separately planned repeat; these samples alone cannot establish broad performance equivalence or universal subtree bounds.

## Verification performed

`python3 -I -S self_check.py` parses Python, checks JavaScript syntax using Node, independently constructs the complete synthetic ordered roster, verifies counts, and rejects seven receipt corruptions. It also verifies that zero timers and accurately reported geometry failures survive as descriptive data. `SELF-CHECK.json` is explicitly synthetic; it is not a browser result. No Firefox process, Gecko build, production edit, or Git operation was run for this artifact.
