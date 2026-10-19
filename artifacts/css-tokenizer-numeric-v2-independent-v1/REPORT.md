# Numeric v2 draft benchmark checkpoint

Status: independent source-bound measurement of the exact draft body SHA4900531c70d9e034e02e2a002c569858843ce6e43f20f835b24be01128d04fb9. This is not acceptance of a final v2 proposal or its length-bound proof. V1 review remains unchanged.

The same benchmark/challenge protocol and inputs were retained from the sealed v1 independent review. Only the candidate numeric body was replaced. Both facade modules now use SourcePosition(usize) and byte_index, matching the actual source accessor shape; the earlier direct usize facade did not compile with the new call. That failed compilation is retained. Complete numeric bodies are unchanged; the bounds-checked/ASCII-name providers remain facades. The source-only checker regenerates these exact changes and binds the body to the complete candidate snapshot.

The 504 independent signed-zero, compensated-magnitude, percentage and incomplete-suffix cases all pass. The draft guard still needs the producer's full short-prefix argument, including rounded integral/fraction accumulation and final f32/percentage output bounds. Finite tests do not discharge that universal contract.

Benchmark: allocation-free noinline wrappers, black_box inputs/results, identical six-input groups, 2.4 million calls/sample, nine samples per variant, alternating order; medians omit the first sample. Rust 1.92 optimized arm64 build. Raw samples and exact sources are retained. No browser or Gecko build.

Run1: integers4.82→5.34ns (+10.8%); fractions4.78→5.51ns (+15.2%); exponents7.48→7.76ns (+3.8%). See BENCHMARK-REPEAT.json for the unchanged repeat. Compared with the separately timed v1, this suggests lower fractional/exponent cost but does not eliminate a normal-path signal. Separate-run noise, frequency, compiler layout, facade substitutions and missing Gecko PGO/LTO prevent browser extrapolation or a precise v1-v2 speedup claim.

Replay `python3 check.py --output /absolute/new/path`; add --benchmark for a new raw timing run without a performance threshold. No final native approval is issued here.

Repeat medians: integers 4.65→5.28ns (+13.6%); fractions 4.77→5.61ns (+17.7%); exponents 7.45→7.81ns (+4.8%).
