# Cold-C A–B–B–A timing interpretation

The candidate has a large Rule-specific cost that increases with chain length. This supports replacing the diagnostic scans before promoting C. It does not establish a precise slowdown percentage, end-user impact, or another release bug.

`compare.py` replayed all four saved raw streams through the frozen callback/report assessors, checked complete reports, native source-role hashes, application metadata, recorded preservation/cleanup and explicit preferences. All passed. This is recorded-evidence verification, not a fresh execution, independent source-to-binary proof or live restoration audit.

Observed median microseconds per update, seven samples per row:

| Rules / mode | A1 before | B1 | B2 | A2 after |
|---|---:|---:|---:|---:|
| 0 / Rule | 6.25 | 6.25 | 6.25 | 6.25 |
| 32 / Rule | 7.50 | 11.25 | 12.50 | 7.50 |
| 64 / Rule | 8.75 | 25.00 | 26.25 | 7.50 |
| 128 / Rule | 13.75 | 77.50 | 88.75 | 8.75 |
| 256 / Rule | 21.25 | 280.00 | 291.25 | 11.25 |
| 256 / literal | 12.50 | 11.25 | 12.50 | 11.25 |
| 256 / Layer | 17.50 | 12.50 | 13.75 | 12.50 |

A is A+B+D; B adds cold C. The candidate Rule divergence recurs in both repetitions, grows with count, leaves the controls comparable, and disappears after restoration. This is consistent with the source-level quadratic scan model, without measuring an exact exponent or native invocation counts.

A1 alone was poor evidence for small timing differences. All 105 batches were 0.08–0.80 ms, on an observed 0.02 ms grid despite the explicit reduced-precision preference being false. This is an observed grid, not independent clock calibration. One grid step divided by sixteen updates is 1.25 microseconds/update. The zero-rule cases generate identical CSS yet their A1 medians span 6.25–13.75 microseconds (2.2x). Across all rows, A1 round medians rose from about 0.12–0.14 ms early to 0.52 ms in round seven. At 256 rules, A1 versus A2 baseline Rule medians differ about 1.9x.

Seven-sample nearest-rank P90 is the maximum sample, not a stable tail estimate. Samples share process and machine history. No concurrent-load, frequency, GC or memory-pressure telemetry accompanies them. Root reported earlier build swapping, but it cannot be assigned as the cause of the drift. Candidate 256-rule median batches are about 4.48 and 4.66 ms, so the gross separation remains useful while baseline denominators remain imprecise.

`COMPARISON.json` retains all fifteen rows, individual-run samples, baseline/candidate median ranges and control drift. Ratio ranges are observed combinations, not confidence intervals. No significance test or performance-acceptance threshold is used.

Next: check an indexed alternative's correctness and run the same two-repetition workload to see whether gross Rule growth disappears. If it approaches baseline, use a separately versioned longer-batch fixture before claiming small improvements or equivalence. Roughly 10–20 ms batches would reduce quantization impact; the current 64-update cap likely remains too short. Choose the same fixed batch length for all builds after a separate pilot, keep bounded counts and value checks, and retain A1/A2 drift controls. Longer batches do not remove machine-load or GC confounders.

The source-path audit in `css-rollback-c-benchmark-path-audit-v1` supports opacity recascade because the reached reset-variable declaration prevents cache insertion and the unique probe has no sharing donor. Getter changes alone do not directly count cold lookups.

Reproduce saved-data analysis with `python3 -I -S -B compare.py --a1 PATH --b PATH --a2 PATH --output artifacts/NEW-COMPARISON.json`. Supply the A1/A2 root runtime directories and the candidate native runtime's `browser` directory. The script authenticates the frozen package and full reports; it runs no browser, build or Git command and reads no live native/application inputs. No existing artifact was changed.
