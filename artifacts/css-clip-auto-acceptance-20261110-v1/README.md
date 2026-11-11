# Clip composition acceptance

The local candidate is accepted for a five-file repair: three native files, the
nine-case WPT, and removal of the existing clip callback's expected-failure
metadata. Research and validation precede that repair. This is one repair of a
known expected-failing behavior, not four newly discovered bugs.

The shared `ClipRect` operation now combines corresponding components, including
matching `auto` values. SMIL's existing restriction remains at its two arithmetic
FFI entry points. The CSS specification trace reaches this composition rule;
the unresolved mixed-auto SVG policy is preserved rather than decided here.

## Evidence

The optimized native build succeeded. The fresh v2 baseline and candidate each
completed 48 WPT callbacks and 5,061 Mochitest callbacks. The three new matching
auto cases and the existing clip iteration callback changed from FAIL to PASS;
every other result stayed the same. All nine new WPT cases pass. Two unrelated
iteration-test failures remain expected. The candidate WPT command exited 1
because the existing clip callback passed against its old failure metadata.
Mochitest exited 0: 5,002 passes, 59 expected todo failures, no unexpected result.
Twelve SVG repeat, sandwich and by-only observations remained identical.

The frozen v2 comparator has a key collision: each Mochitest page's first null-
named callback is overwritten by its harness result. Independent review found
this by reconciling the result counts. The corrected raw-log comparison includes
all 5,116 callback/harness rows and the complete 5,061-message Mochitest inventory.
It passes with exactly the four intended improvements. Root replayed that check
and four synthetic controls demonstrating that the old comparison misses a
changed first callback and the corrected comparison detects it. The immutable
v2 receipts retain their original 5,112-row result; use the independent review
for the complete comparison. No browser rerun is needed to recover retained raw
events. Future runner reuse must fix this collision.

The earlier v1 run's failure was a separate harness adapter mistake: Mochitest
ends with PASS, while WPT ends with OK. Its raw logs and successful restoration
remain recorded. V2 corrects that adapter and reruns the baseline.

Root and independent review authenticated restoration of all 9,379 application
entries and the three native sources. The independent review also checked the
three build/test extras and 61 test-source pins. Root checked the staged Git
entries, unchanged HEAD, fixture removal and process-group termination. The
owned 1,008,658,825-byte backup was removed after verified restoration. Build
intermediate objects are not claimed to be restored.

## Formal contribution and limits

The source audit and expected-failure triage identified the defect. Lean did not
discover it automatically. The independent model proves relocation of the SMIL
guard for arbitrary pure, total component computations and arithmetic operations,
including count zero, outer auto, mismatches and unchanged preparation state.
Root replayed 14 audited declarations and four rejected false claims. The
concrete native purity/totality correspondence is source-reviewed, not extracted
or mechanically proved. Floating-point arithmetic and compiler/FFI behavior are
outside that proof.

This is bounded local acceptance. Debug/sanitizer execution, direct native
count-zero calls, a full animation/SMIL suite, isolated upstream application and
release-channel exposure remain untested. The gate reassessment found no new
assertion-sensitive path in this repair; it does not waive the separate debug
gate for a future missing-pseudo CSSOM repair. No security impact is asserted.

## Receipts

- [Candidate and source audit](../css-clip-auto-candidate-20261110-v1/REPORT.md)
- [Independent proof and gate assessment](../css-clip-auto-candidate-review-20261110-v1/GATE-REASSESSMENT.md)
- [Frozen v2 experiment](../css-clip-auto-runtime-20261110-v2/README.md)
- [Complete independent comparison](../css-clip-auto-runtime-review-20261110-v1/CHECK.json)
- [Comparator collision controls](../css-clip-auto-runtime-review-20261110-v1/CONTROLS.json)
- [Root restoration check](../css-clip-auto-runtime-20261110-v2/candidate1/ROOT-RESTORATION.json)
