# Standalone commitStyles cost parser

`analyze.py` reads the unfiltered WPT raw JSONL contract for the sealed local benchmark. It does not launch anything, validate live state, or grant native/performance acceptance.

```sh
python3 -I -S -B artifacts/css-keyframe-commit-styles-cost-analysis-v2/analyze.py \
  --raw /ABSOLUTE/RAW.jsonl --output /ABSOLUTE/ABSENT/OUTPUT
```

The output directory must be absent. A successful parse writes the exact input bytes as RAW.jsonl, the complete decoded DATASET.json (all 54 rows and 54 cleanup records), and SUMMARY.json. Each of the six cases has separate warmup and measured API/flush/total samples, median, minimum and maximum. All 12 warmup and 42 measured rows remain; nothing is filtered. There are no thresholds, causal comparisons, control subtraction or inferred performance acceptance.

The parser requires one suite, one exact selected test, the exact calibration subtest PASS, harness OK, compatible expected status and no intermittent allowances. It rejects crashes, native assertions and structured infrastructure errors. An all-zero assertion-count record is allowed. It accepts the one console result arriving after test_end or suite_end in the finalized log because process-output delivery can lag harness events; the actual selected test must have started first.

Console decoding is deliberately narrow: raw event JSON → double-quoted `console.log` string → ASCII success-prefix JSON payload. Duplicate JSON keys and nonstandard NaN/Infinity constants reject at every layer. No logged JavaScript is evaluated. Any incomplete marker, multiple/missing result, malformed/truncated envelope, invalid config/case/order/count, pending/failed calibration, nonfinite/negative timing, inconsistent binary64 subtraction results or unsuccessful cleanup rejects the dataset. The success payload must match the original six-case round rotation and exact schema. An absent success message cannot be rescued by a harness PASS.

The recorded process ID and command must be present and are retained, but this parser does not authenticate them against a build, browser executable or root execution receipt. The parent capture/review must join source/binary identity, actual exit, resource/metadata preservation and process cleanup separately. Similarly, the data declares page cleanup and correctness; this parser checks that exact schema alongside the successful harness, not native/browser behavior independently. Missing output after a process crash is failure, not a zero-time sample.

Inherited synthetic validation passed again (cb6964, exit 0): four valid controls and 44 rejected corruptions. Positives include delayed stdout delivery, zero durations and a retained large finite sample. Controls cover quoting/JSON envelopes, dataset uniqueness and row/calibration/cleanup invariants, missing or failed harness records and infrastructure faults. `CHECK.json` is **synthetic parser evidence only**; no real browser capture or timing result is bound. The raw source file is never modified, including on rejection; a failed parse creates no purported successful output dataset.

To rerun only the inert checks:

```sh
python3 -I -B -c "import runpy,sys; sys.path.insert(0,'artifacts/css-keyframe-commit-styles-cost-analysis-v2'); runpy.run_path('artifacts/css-keyframe-commit-styles-cost-analysis-v2/check.py',run_name='__main__')"
```

REFERENCES pins the unchanged HTML/manifest and the source-supported console output contract. The future raw file and actual execution remain unbound. No browser, server, compiler, build, native/index edit or runner framework was added.

## Narrow v2 correction

V1 remains sealed. DELTA.patch changes only the numerical addition gate, adds its helper and imports Fraction. The seven other functions, including raw-envelope/harness parsing and descriptive summaries, are AST-identical; all 44 malformed-data controls still reject and all four positive controls pass.

Node binary64 subtraction provides a valid ordered counterexample, in milliseconds:

- begin = 1.000001; afterAPI = 3.14159; afterFlush = 10.3.
- apiMs = 2.1415889999999997; flushMs = 7.158410000000001.
- totalMs = 9.299999000000001, but the rounded addition apiMs + flushMs = 9.299999.

Thus exact equality incorrectly rejects a possible correctly measured row. These are JavaScript arithmetic witnesses, not observed browser timings. Seven Node vectors include two such counterexamples plus zero, equal timestamps, dyadic, smallest-subnormal and maximum-finite boundaries. All seven pass v2 unchanged; both counterexamples reject in v1. Three inconsistent triples reject, including the first witness with total moved one representable step upward beyond its bound, a 1e-12 corruption, and an overflowing sum. NUMERIC-CHECK records this regression test (3cb614, exit 0).

Let the exact real differences of the three represented timestamps be x=b−a, y=c−b and z=c−a; x+y=z. Their recorded binary64 results A,F,T are each round-to-nearest results. Each rounding error is bounded by half the output ULP (conservative at binade boundaries). Therefore |A+F−T| ≤ (ULP(A)+ULP(F)+ULP(T))/2 is a necessary consistency condition. The helper evaluates this inequality with exact Fractions of the recorded binary64 values, so it does not add a fourth floating-point rounding from the comparison sum. Fraction arithmetic also avoids overflowing that sum or underflowing the half-ULP budget at the smallest subnormal. This is a format-derived consistency bound, not an arbitrary absolute/relative timing tolerance or performance threshold. It does not prove the unrecorded timestamps existed or the timing was measured faithfully.

Inputs must still be finite nonnegative numbers with the exact semantic/lifecycle schema. Values are converted to binary64 only for this check, reflecting JavaScript Number serialization; no stored raw value, sample, summary input or source log is rounded, replaced or filtered. There is no assumption that timer precision is integral milliseconds or that all timestamps lie in one Sterbenz-exact range.

COMMAND-TYPE-EVIDENCE independently records archived actual WPT output: candidate has 26 process_output records (20 numeric browser PIDs), restored has 46 (40 browser PIDs). Every command is a string; browser process IDs are decimal strings. The twelve other records are certutil output. These are archived transport examples, not benchmark measurements or new root/current-state verification. The parser's string command requirement therefore remains unchanged.
