# Independent CSSOM rectangle runtime review

## Recommendation

**Accept the bounded runtime evidence for two independently testable repairs.** The DOMRect publication patch and ordinary integer-translation patch each repair their own standalone witnesses. Neither alone closes every combined case. This review does not establish the full safe-origin F1–F12 contract, all-frame geometry equivalence, universal floating-point correctness, or performance acceptability.

I previously reviewed the native proposal and authored the split diagnostic tests, but did not implement either native repair or run these browser experiments. The present work independently reconstructs the raw results and validates source/test/binary bindings. Test authorship is disclosed; this is not an independent invention of the split oracle.

## Combined matrix

| Actual variant | New 28 tests | Existing 29 subtests | File outcomes |
|---|---|---|---|
| Baseline | 12 PASS / 16 FAIL | 27 PASS / 2 expected FAIL | 13 OK / 1 PASS |
| DOMRect only | 20 PASS / 8 FAIL | unchanged | unchanged |
| Integer path only | 16 PASS / 12 FAIL | unchanged | unchanged |
| Both | 28 PASS | unchanged | unchanged |

The analyzer predicts each named case separately: eight small and four coordinate-effect controls always pass; eight exponent-boundary cases need the DOMRect fix; four large integer-host cases need the integer path; four large fractional-host cases need both. It compares complete unique outcome-key rosters, raw events with RUN summaries, status/expected/intermittent fields, and source snapshots with the exact original/candidate proposal. Passing status is not a blanket equality of failure messages or every observed numeric value.

All runs retain 59 stable pins. Only the designated source file(s), Firefox executable and XUL differ across variants. All three candidate builds and restoration exit 0; source, HEAD and index restoration are recorded. The two existing expected failures concern rotated SVG text/Range geometry and trailing surrogate indexing; their retained WPT metadata agrees. Existing failures are not counted as repaired or unexpected.

## Standalone matrix

| Actual variant | New 8 tests | Existing 66 subtests | File outcomes |
|---|---|---|---|
| Baseline | 4 PASS / 4 FAIL | 64 PASS / 2 expected FAIL | 22 OK / 1 PASS |
| DOMRect only | 6 PASS / 2 FAIL | unchanged | unchanged |
| Integer path only | 6 PASS / 2 FAIL | unchanged | unchanged |
| Both | 8 PASS | unchanged | unchanged |

The identity-transform fixture keeps the integer fast path ineligible and isolates DOMRect conversion. The untransformed fixture isolates the integer-path repair at a numeric point where the old DOMRect setter already preserves the requested end after an exact layout rectangle. Each includes horizontal/vertical and small/large controls, containing-edge/marker/size calibration and both rectangle APIs. The runtime test bytes differ from my retained split drafts only in two titles and two assertion messages, explicitly enumerated by the analyzer. All assertions and input values are unchanged.

The 23-file standalone run expands regression coverage to 3D contexts, SVG foreignObject, inline/block rectangles, iframe hit testing, ResizeObserver and IntersectionObserver. All 86 pins are stable within each run; cross-variant source/binary differences are exactly the expected ones. Builds, restoration and WPT lint exit 0. Default formatting exit 0 hid a helper-signature warning; the retained detailed log identifies it. A separately formatted candidate/performance experiment is outside this review until its exact transfer is checked.

## Observation precision and remaining boundaries

All 56 diagnostic rows have ResizeObserver callbacks. Their borderBoxSize/contentBoxSize arrays are unchanged across variants. This does **not** mean the entire ResizeObserver object is unchanged: DOMRect-only and both change contentRect in exactly 28 rows, while integer-only changes none. The changed contentRect results agree between DOMRect-only and both.

For example, the large ordinary box retains reported border/content size 139808.140625, while contentRect width changes from 139808.15625 to 139808.14999389648. The retained complete SetContentRectAndSize body constructs an app-unit nsRect from the CSS size before calling SetLayoutRect, while publishing size arrays directly. This explains a distinct shared DOMRect consumer; it is not evidence of changed actual layout dimensions or a proof that all ResizeObserver precision is repaired.

For the four large non-flex rows (two axes, with/without padding), bounding ends are baseline 100.015625, DOM-only 100.01666259765625, integer-only/both 100; marker ends remain 100. DOM-only exposes the remaining graphics conversion error more directly and is numerically farther from 100 here. No formerly passing test fails, but universal improvement in numerical distance is not claimed. The 48 supplementary flex/table/replaced rows remain diagnostics, not a new asserted caption-union oracle.

The browser builds include the pinned preexisting local changes. This is actual variant isolation within that shared build, not isolated upstream, cross-platform, performance or release validation. Finite regression success does not establish every transformed/SVG/perspective/root path. The native proposal review and numeric component retain actual frame/matrix/provider/lifetime, clipping, union and machine-domain boundaries. No tolerance theorem replaces the original exact containment obligation.

## Recheck

`python3 -I -S analyze.py` reconstructs the first matrix and probe from 253 consumed inputs. `python3 -I -S analyze_standalone.py` reconstructs the second from 339 inputs. Their receipts retain exact input hashes; use `--check` to compare without rewriting. Root authorized this reviewer to add the standalone COMPARISON/REPORT and seal after the experiment was terminal and restored. All raw logs and executed inputs remain unchanged. The final verification script authenticates the sealed runtime rosters and these review inputs before rerunning analyzers. It performs no browser, native build or Git operation.
